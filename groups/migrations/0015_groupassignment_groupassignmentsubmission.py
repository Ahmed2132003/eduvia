from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0014_groupchatmessage_attachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='group_assignments/attachments/')),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('max_grade', models.PositiveIntegerField(default=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='groups.teachergroup')),
            ],
            options={
                'ordering': ['-due_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GroupAssignmentSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='group_assignments/submissions/')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('grade', models.PositiveIntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='groups.groupassignment')),
                ('graded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_assignment_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='groupassignmentsubmission',
            unique_together={('assignment', 'student')},
        ),
    ]