from django import template

register = template.Library()

@register.filter
def contains(value, arg):
    return arg in value

@register.filter
def drive_id(value):
    import re
    match = re.search(r'/d/([^/]+)', value)
    return match.group(1) if match else value

@register.filter
def lookup(dict, key):
    return dict.get(str(key))

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, ZeroDivisionError):
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