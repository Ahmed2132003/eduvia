from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0016_grouptodoitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouptodoitem',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
    ]