from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_remove_userprofile_subscription_end_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('order', models.PositiveIntegerField(default=0)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sections',
                    to='courses.course',
                )),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('lesson_type', models.CharField(
                    choices=[
                        ('video', 'Video Lesson'),
                        ('text', 'Text Lesson'),
                        ('article', 'Article'),
                    ],
                    default='video',
                    max_length=20,
                )),
                ('order', models.PositiveIntegerField(default=0)),
                # Video fields
                ('video_url', models.URLField(blank=True, null=True, max_length=500)),
                ('video_duration', models.FloatField(
                    default=0,
                    help_text='Duration in minutes',
                )),
                ('is_preview', models.BooleanField(
                    default=False,
                    help_text='Free preview lesson visible before enrollment',
                )),
                # Text / Article fields
                ('content', models.TextField(blank=True)),
                # Description (shared)
                ('description', models.TextField(blank=True)),
                ('section', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lessons',
                    to='courses.section',
                )),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('current_time', models.FloatField(default=0.0)),
                ('progress_percentage', models.FloatField(default=0.0)),
                ('lesson', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress',
                    to='courses.lesson',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lesson_progress',
                    to='accounts.user',
                )),
            ],
            options={
                'unique_together': {('user', 'lesson')},
            },
        ),
    ]
