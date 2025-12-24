from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from stories.models import Episode, Cut
from library.models import UserViewedEpisode
from django.utils import timezone
import random

def episode_detail_view(request, episode_id):
    user = request.user if request.user.is_authenticated else None
    episode = get_object_or_404(Episode, id=episode_id)

    # 컷 4개 가져오기
    cuts = episode.cuts.all()[:4]

    # 같은 역(Webtoon의 Station)에 속한 다른 에피소드
    station = episode.webtoon.station
    all_episodes = Episode.objects.filter(webtoon__station=station)
    other_episodes = all_episodes.exclude(id=episode.id)

    # 저장 상태 (is_saved)
    is_saved = False
    if user:
        uve = UserViewedEpisode.objects.filter(user=user, episode=episode).first()
        if uve and uve.saved:
            is_saved = True

    # 새 에피 버튼 처리 (이미 본 적 있는지)
    new_episode_button = False
    if user:
        viewed_episodes = UserViewedEpisode.objects.filter(
            user=user, episode__webtoon__station=station
        )

        # GET param으로 다음 에피 선택
        if request.GET.get('next') == 'true':
            unseen_episodes = Episode.objects.filter(webtoon__station=station).exclude(
                id__in=viewed_episodes.values_list('episode_id', flat=True)
            )
            if unseen_episodes.exists():
                episode = random.choice(list(unseen_episodes))
                cuts = episode.cuts.all()[:4]  # 컷 갱신

        new_episode_button = viewed_episodes.exists()

    # ==========================
    # UserViewedEpisode 안전하게 생성
    # ==========================
    if user and episode.webtoon and episode.webtoon.station:
        UserViewedEpisode.objects.get_or_create(
            user=user,
            episode=episode,
            station=episode.webtoon.station
        )

    context = {
        'episode': episode,
        'cuts': cuts,
        'other_episodes': other_episodes,
        'new_episode_button': new_episode_button,
        'is_saved': is_saved,
    }
    return render(request, 'stories/episode_detail.html', context)



# ===== 저장 토글 뷰 =====
@login_required
def toggle_saved(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    uve, created = UserViewedEpisode.objects.get_or_create(user=request.user, episode=episode)
    
    if uve.saved:
        uve.saved = False
        uve.saved_at = None
    else:
        uve.saved = True
        uve.saved_at = timezone.now()
    
    uve.save()
    return redirect('episode_detail', episode_id=episode_id)
