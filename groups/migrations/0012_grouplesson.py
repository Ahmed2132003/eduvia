from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    # آخر migration معروفة في تطبيق groups حسب كل التوثيق المتاح
    # (Part 26 — نسخة معدّلة، Manual Recording Upload).
    # ⚠️ زي كل migration مكتوبة يدويًا في المشروع: لازم تشغّل
    # `python manage.py makemigrations --check --dry-run` فعليًا على
    # السيرفر قبل `migrate`، للتأكد إن آخر migration فعلية موجودة عندك
    # لسه هي 0011_grouplivesession_manual_recording_fields — لو فيه
    # migration أحدث اتعملت ومش موثقة هنا، لازم تعدّل dependencies تحت.
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0011_grouplivesession_manual_recording_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupLesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('video_url', models.URLField(blank=True, max_length=500, null=True)),
                ('video_duration', models.FloatField(default=0, help_text='مدة الفيديو بالدقايق (بتتكتب يدويًا من المدرس)')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
                ('publish_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='groups.teachergroup')),
            ],
            options={
                'ordering': ['order', 'created_at'],
            },
        ),
    ]