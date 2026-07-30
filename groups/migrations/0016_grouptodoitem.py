from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0015_groupassignment_groupassignmentsubmission'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupTodoItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('due_at', models.DateTimeField(blank=True, null=True)),
                ('is_done', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todo_items', to='groups.teachergroup')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todo_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['is_done', 'due_at', '-created_at'],
            },
        ),
    ]