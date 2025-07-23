from django import template
from django.utils.text import slugify
import re
import logging

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def custom_slugify(value):
    """
    تنظيف النص وإنشاء slug صالح مع دعم الأحرف العربية.
    إذا كان النص فارغًا أو ينتج slug فارغ، يتم إرجاع 'default-title'.
    """
    if not value or not value.strip():
        logger.debug(f"Empty or invalid title received: {value}")
        return 'default-title'
    # تنظيف النص من الأحرف غير المدعومة مع السماح بالأحرف العربية
    cleaned_text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', str(value)).strip()
    result = slugify(cleaned_text, allow_unicode=True)
    logger.debug(f"Slugified title: {value} -> {result}")
    return result or 'default-title'