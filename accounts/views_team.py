from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.conf import settings

# 모델 임포트
from .models import MembershipRequest, Team, TeamMember
from library.models import Bookmark

# 인증 클래스 재정의 (임포트 순환 방지)
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return 

def get_image_url(ep):
    from django.conf import settings
    try:
        if ep.cuts.exists():
            first_cut = ep.cuts.first()
            # DB에 저장된 실제 문자열 경로 (예: 'media/webtoons/...')
            raw_path = str(first_cut.image).lstrip('/')
            base_url = settings.MEDIA_URL.rstrip('/') # 보통 '/media'
            
            # 경로 중복 체크 로직
            # base_url의 끝 단어(media)가 raw_path의 시작과 겹치는지 확인
            media_folder_name = base_url.split('/')[-1] # 'media' 추출
            
            if raw_path.startswith(media_folder_name + '/'):
                # 중복된다면 raw_path에서 'media/' 부분을 떼어냄
                clean_path = raw_path[len(media_folder_name)+1:]
                return f"{base_url}/{clean_path}"
            
            return f"{base_url}/{raw_path}"
    except Exception:
        pass
    return "https://via.placeholder.com/150"

@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_team_shared_bookmarks(request):
    """팀 정보 및 팀원 활동 내역 조회"""
    user = request.user
    team = Team.objects.filter(Q(leader=user) | Q(members__user=user)).distinct().first()
    
    if not team:
        return Response({"success": True, "has_team": False})

    is_leader = (team.leader == user)
    
    # 팀 멤버 데이터 구성
    members_data = []
    # 1. 팀장 데이터
    members_data.append({
        "username": team.leader.username,
        "is_leader": True,
        "bookmarks": [{
            "id": b.episode.episode_id,
            "title": b.episode.subtitle,
            "imageUrl": get_image_url(b.episode)
        } for b in Bookmark.objects.filter(user=team.leader).select_related('episode')]
    })
    
    # 2. 팀원들 데이터
    for tm in team.members.all().select_related('user'):
        members_data.append({
            "username": tm.user.username,
            "is_leader": False,
            "bookmarks": [{
                "id": b.episode.episode_id,
                "title": b.episode.subtitle,
                "imageUrl": get_image_url(b.episode)
            } for b in Bookmark.objects.filter(user=tm.user).select_related('episode')]
        })

    # 3. 팀장용 대기 신청 목록
    pending_members = []
    if is_leader and user.leader_code:
        pending_qs = MembershipRequest.objects.filter(
            target_leader_code=user.leader_code, 
            status='PENDING'
        ).order_by('-created_at')
        
        pending_members = [{
            "id": p.id, 
            "applicant_name": p.applicant_name, 
            "date": p.created_at.strftime('%Y-%m-%d')
        } for p in pending_qs]

    return Response({
        "success": True,
        "has_team": True,
        "team_name": team.name,
        "is_leader": is_leader,
        "team_code": team.team_code,
        "members_data": members_data,
        "pending_members": pending_members
    })

@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def handle_team_request(request, request_id):
    """팀장의 승인 시 자동으로 TeamMember 테이블에 등록"""
    action = request.data.get('action') # 'APPROVE' or 'REJECT'
    req = get_object_or_404(MembershipRequest, id=request_id)
    
    # 권한 체크: 현재 로그인한 유저가 해당 팀의 팀장인지 확인
    if req.target_leader_code != request.user.leader_code:
        return Response({"success": False, "message": "권한이 없습니다."}, status=403)

    if action == 'APPROVE':
        # 1. 신청서 상태 변경
        req.status = 'APPROVED'
        req.save()
        
        # 2. 자동 승인 처리: TeamMember 테이블에 즉시 추가
        team = Team.objects.get(team_code=req.target_leader_code)
        TeamMember.objects.get_or_create(team=team, user=req.user)
        
        return Response({"success": True, "message": f"{req.user.username} 님이 팀원으로 등록되었습니다."})
    
    elif action == 'REJECT':
        req.status = 'REJECTED'
        req.save()
        return Response({"success": True, "message": "신청을 반려했습니다."})
    
    
# accounts/views_team.py (기존 코드에 아래 함수 추가)

@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def membership_request_view(request):
    """팀원 신청 시 팀명과 팀 코드를 엄격히 대조"""
    data = request.data
    request_type = data.get('request_type')
    
    # 팀원 신청(MEMBER)인 경우 검증 로직 추가
    if request_type == 'MEMBER':
        target_code = data.get('target_leader_code')
        target_team_name = data.get('team_name')
        
        # DB에서 해당 코드와 팀명이 일치하는 팀이 있는지 확인
        team_exists = Team.objects.filter(team_code=target_code, name=target_team_name).exists()
        
        if not team_exists:
            return Response({
                "success": False, 
                "message": "팀명 또는 팀 코드가 일치하는 팀을 찾을 수 없습니다. 다시 확인해주세요."
            }, status=400)

    # 검증 통과 시 신청서 생성
    try:
        MembershipRequest.objects.create(
            user=request.user,
            request_type=request_type,
            team_name=data.get('team_name'),
            applicant_name=data.get('applicant_name'),
            target_leader_code=data.get('target_leader_code', ''),
            status='PENDING'
        )
        return Response({"success": True, "message": "신청이 완료되었습니다."})
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=400)