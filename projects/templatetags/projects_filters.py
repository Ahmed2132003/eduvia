from django import template
import re
from django.utils.text import slugify
import unicodedata

register = template.Library()

@register.filter(name='contains')
def contains(value, arg):
    """Check if the value contains the given substring."""
    if value is None:
        return False
    return arg in str(value)

@register.filter(name='drive_id')
def drive_id(value):
    """Extract Google Drive file ID from URL."""
    if value is None:
        return ""
    match = re.search(r'[-\\w]{25,}', str(value))
    return match.group(0) if match else ""

@register.filter(name='lookup')
def lookup(dict, key):
    """Get value from dictionary by key."""
    return dict.get(str(key))

@register.filter(name='div')
def div(value, arg):
    """Divide value by arg, handle errors."""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='mul')
def mul(value, arg):
    """Multiply value by arg, handle errors."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='count_true')
def count_true(value):
    """Count number of True values in a list."""
    return sum(1 for x in value if x)

@register.filter(name='custom_slugify')
def custom_slugify(value):
    """Convert string to a URL-safe slug."""
    print(f"Slugify input: {value}")  # لتسجيل القيمة المدخلة
    if not value:
        print("Slugify returning default: no-title")
        return 'no-title'
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    slug = slugify(value)
    print(f"Slugify output: {slug}")  # لتسجيل القيمة الناتجة
    return slug if slug else 'no-title'