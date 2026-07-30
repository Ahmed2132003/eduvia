import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0003_alter_livesession_session_image'),
        ('groups', '0007_teachergroup_join_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='livesession',
            name='group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='live_sessions',
                to='groups.teachergroup',
            ),
        ),
    ]