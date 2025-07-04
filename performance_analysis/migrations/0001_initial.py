# Generated by Django 5.2 on 2025-07-02 22:30

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('recommended_at', models.DateTimeField(auto_now_add=True)),
                ('priority', models.PositiveIntegerField(default=1)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['priority', '-recommended_at'],
            },
        ),
        migrations.CreateModel(
            name='PerformanceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_id', models.CharField(default=uuid.uuid4, max_length=36, unique=True)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('performance_summary', models.TextField()),
                ('recommendations', models.TextField()),
                ('emailed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_courses', models.PositiveIntegerField(default=0)),
                ('completed_videos', models.PositiveIntegerField(default=0)),
                ('total_coins', models.PositiveIntegerField(default=0)),
                ('avg_viewing_time', models.FloatField(default=0)),
                ('interaction_rate', models.FloatField(default=0)),
                ('strength_areas', models.TextField(blank=True)),
                ('weakness_areas', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='performance', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_id', models.CharField(max_length=36, unique=True)),
                ('report_file', models.FileField(upload_to='reports/')),
                ('generated_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
