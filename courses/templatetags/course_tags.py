# courses/templatetags/course_tags.py

from django import template
from django.utils.text import slugify
from courses.models import VideoProgress
import re
import logging
from django.urls import reverse

logger = logging.getLogger(__name__)

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


@register.filter
def custom_slugify(value):
    """
    Slugify with full Arabic + English support.
    Falls back to 'course-{id}' if title is empty or invalid.
    """
    if not value or not str(value).strip():
        logger.debug(f"Empty title in custom_slugify: {value}")
        return 'default-title'
    
    # Use Django's slugify with allow_unicode=True
    result = slugify(str(value), allow_unicode=True)
    
    if not result or result == '':
        logger.debug(f"Slugify returned empty for: {value}")
        return 'default-title'
    
    # Clean extra dashes
    result = re.sub(r'-+', '-', result.strip('-'))
    logger.debug(f"custom_slugify: '{value}' -> '{result}'")
    return result


@register.filter
def contains(value, arg):
    return arg in value


@register.filter
def drive_id(value):
    match = re.search(r'/d/([^/]+)', value)
    return match.group(1) if match else value


@register.filter
def lookup(dict, key):
    return dict.get(str(key))


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def count_true(value):
    return sum(1 for x in value if x)


# === NEW: Safe Arabic Slug for URLs (Main Fix) ===
@register.filter
def arabic_slug(value, fallback_id=None):
    """
    Generate URL-safe slug for Arabic & English titles.
    If title is empty or slugify fails → use fallback_id or 'course'
    """
    if not value or not str(value).strip():
        return str(fallback_id) if fallback_id else 'course'
    
    slug = slugify(str(value), allow_unicode=True)
    
    if not slug:
        return str(fallback_id) if fallback_id else 'course'
    
    slug = re.sub(r'-+', '-', slug.strip('-'))
    return slug

@register.simple_tag
def course_url(course):
    return reverse('courses:course_details', kwargs={
        'course_id': course.id,
        'course_slug': course.slug
    })

@register.simple_tag
def video_url(video):
    return reverse('courses:watch_video', kwargs={
        'course_id': video.course.id,
        'course_slug': video.course.slug,
        'video_id': video.id,
        'video_slug': video.slug
    })
    
@register.simple_tag
def enroll_url(course):
    """يولّد رابط التسجيل في الكورس مع fallback slug آمن."""
    return reverse('courses:enroll_course', kwargs={
        'course_id': course.id,
        'course_slug': arabic_slug(course.title, fallback_id=course.id)
    })