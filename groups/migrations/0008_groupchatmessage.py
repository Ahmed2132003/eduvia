import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0007_teachergroup_join_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                (
                    'group',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='chat_messages',
                        to='groups.teachergroup',
                    ),
                ),
                (
                    'sender',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['sent_at'],
            },
        ),
    ]