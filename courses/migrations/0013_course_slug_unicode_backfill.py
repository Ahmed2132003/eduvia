from django.db import migrations, models
from django.utils.text import slugify
import re


def make_slug(title, pk):
    base = slugify(str(title or ''), allow_unicode=True)
    base = re.sub(r'-+', '-', base).strip('-')
    return base or f'course-{pk}'


def backfill_course_slugs(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course in Course.objects.all().order_by('id'):
        base = make_slug(course.title, course.pk)
        candidate = base
        i = 2
        while Course.objects.exclude(pk=course.pk).filter(slug=candidate).exists():
            candidate = f"{base}-{i}"
            i += 1
        course.slug = candidate
        course.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_merge_20260514_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=500, unique=True),
        ),
        migrations.RunPython(backfill_course_slugs, migrations.RunPython.noop),
    ]