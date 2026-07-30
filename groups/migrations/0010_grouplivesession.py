import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    # آخر migration في تطبيق groups وقت كتابة الجزء ده كانت
    # 0009_groupsubscription_reminder_flags (Part 16). لو عندك migration
    # أحدث اتعملت بعد كده على السيرفر الحقيقي (خارج الملفات اللي
    # اتبعتلي في الجلسة دي)، غيّر السطر ده ليطابق آخر migration فعلية
    # عندك قبل ما تشغل makemigrations/migrate.
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0009_groupsubscription_reminder_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupLiveSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('mode', models.CharField(
                    choices=[('camera', 'camera'), ('screen_share', 'screen_share'), ('both', 'both')],
                    default='camera',
                    max_length=20,
                )),
                ('status', models.CharField(
                    choices=[
                        ('scheduled', 'scheduled'),
                        ('live', 'live'),
                        ('ended', 'ended'),
                        ('canceled', 'canceled'),
                    ],
                    default='scheduled',
                    max_length=20,
                )),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('room_identifier', models.CharField(blank=True, max_length=100, unique=True)),
                ('recording_url', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='group_live_sessions',
                    to='groups.teachergroup',
                )),
                ('host', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-scheduled_at', '-created_at'],
            },
        ),
    ]