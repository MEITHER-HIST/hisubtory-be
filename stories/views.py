from django.shortcuts import render
from django.http import JsonResponse
from .services import generate_story_from_db

def create_story_api(request, station_id):
    story = generate_story_from_db(station_id)
    
    if story:
        return JsonResponse({
            "status": "success",
            "story_id": story.id,
            "images": [story.image_1.url, story.image_2.url, story.image_3.url, story.image_4.url],
            "captions": [story.caption_1, story.caption_2, story.caption_3, story.caption_4]
        })
    else:
        return JsonResponse({"status": "error", "message": "생성 실패"}, status=500)