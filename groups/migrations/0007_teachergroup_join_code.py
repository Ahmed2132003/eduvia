import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_groupupgrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachergroup',
            name='join_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]