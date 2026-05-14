# courses/utils.py
import re
def clean_text(text):
    if not text:
        return 'default'
    return re.sub(r'[^\w\s-]', '', text).strip() or 'default'