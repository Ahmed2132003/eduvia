from django import template
from courses.models import VideoProgress

register = template.Library()

@register.filter
def in_video_progress(video_id, user):
    return VideoProgress.objects.filter(video_id=video_id, user=user, completed=True).exists()

@register.filter
def is_video_unlocked(video, user):
    """
    Check if a video is unlocked for a user based on their progress.
    The first video is always unlocked, and subsequent videos are unlocked
    if the previous video is completed.
    """
    videos = video.course.videos.order_by('order')
    if video.order == 1:  # First video is always unlocked
        return True
    previous_video = videos.filter(order=video.order - 1).first()
    if not previous_video:
        return False
    previous_progress = VideoProgress.objects.filter(user=user, video=previous_video).first()
    return previous_progress and previous_progress.completed
