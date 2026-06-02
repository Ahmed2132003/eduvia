from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_remove_userprofile_subscription_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='course_images/'),
        ),
    ]