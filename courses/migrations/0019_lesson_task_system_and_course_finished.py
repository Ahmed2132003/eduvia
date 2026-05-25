import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_lesson_comments_ratings_attachments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ── 1. Course.is_finished ─────────────────────────────────────────────
        migrations.AddField(
            model_name='course',
            name='is_finished',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Instructor marks the course as completed/finished. '
                    'Required (together with all lessons done) for certificate eligibility.'
                ),
            ),
        ),

        # ── 2. LessonTask ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='LessonTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(
                    max_length=20,
                    choices=[
                        ('mcq',           'Multiple Choice (MCQ)'),
                        ('essay',         'Essay / Open Answer'),
                        ('file_upload',   'File Upload'),
                        ('external_link', 'External Link'),
                    ],
                    default='mcq',
                )),
                ('title',        models.CharField(max_length=300)),
                ('description',  models.TextField(blank=True)),
                ('questions',    models.JSONField(default=list)),
                ('passing_score', models.PositiveSmallIntegerField(default=70)),
                ('external_url', models.URLField(blank=True)),
                ('order',        models.PositiveIntegerField(default=0)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('lesson', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='task',
                    to='courses.lesson',
                )),
            ],
            options={'ordering': ['order']},
        ),

        # ── 3. LessonTaskSubmission ───────────────────────────────────────────
        migrations.CreateModel(
            name='LessonTaskSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('attempt_number',       models.PositiveSmallIntegerField(default=1)),
                ('submitted_answers',    models.JSONField(default=list)),
                ('essay_answer',         models.TextField(blank=True)),
                ('file_url',             models.URLField(blank=True)),
                ('external_url_visited', models.BooleanField(default=False)),
                ('score',   models.FloatField(default=0.0)),
                ('passed',  models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='submissions',
                    to='courses.lessontask',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lesson_task_submissions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-submitted_at']},
        ),
    ]