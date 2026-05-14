import re
from django.utils.text import slugify


def clean_text(text):
    if not text:
        return 'default'
    return re.sub(r'[^\w\s-]', '', str(text)).strip() or 'default'


def generate_unicode_slug(value, fallback_prefix='course', fallback_id=None):
    """Generate SEO-safe unicode slug (Arabic/English), with deterministic fallback."""
    base = slugify(str(value or ''), allow_unicode=True)
    base = re.sub(r'-+', '-', base).strip('-')
    if base:
        return base
    if fallback_id is not None:
        return f"{fallback_prefix}-{fallback_id}"
    return fallback_prefix


def unique_model_slug(model_cls, value, fallback_prefix='course', fallback_id=None, instance_pk=None, slug_field='slug'):
    base = generate_unicode_slug(value, fallback_prefix=fallback_prefix, fallback_id=fallback_id)
    candidate = base
    i = 2
    qs = model_cls.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(**{slug_field: candidate}).exists():
        candidate = f"{base}-{i}"
        i += 1
    return candidate