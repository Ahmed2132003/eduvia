from django import template
import re

register = template.Library()

@register.filter
def custom_slugify(value):
    """
    Convert text to a URL-safe slug.
    Removes special characters, converts spaces to hyphens, and converts to lowercase.
    """
    text = str(value).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text