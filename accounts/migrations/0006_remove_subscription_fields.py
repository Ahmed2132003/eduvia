from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_subscription_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='subscription_plan',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='subscription_end_date',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='subscription_duration',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='stripe_customer_id',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='stripe_subscription_id',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='paymob_order_id',
        ),
    ]
