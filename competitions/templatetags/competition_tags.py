from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def localtime(value):
    return timezone.localtime(value).strftime('%B %d, %Y, %I:%M %p')