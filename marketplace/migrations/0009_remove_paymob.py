from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0008_alter_wallettransaction_payment'),
    ]

    operations = [
        # 1. Remove FK from WalletTransaction to CoursePayment before dropping the table
        migrations.RemoveField(
            model_name='wallettransaction',
            name='payment',
        ),

        # 2. Drop RevenueShare (depends on CoursePayment)
        migrations.DeleteModel(
            name='RevenueShare',
        ),

        # 3. Drop CoursePayment
        migrations.DeleteModel(
            name='CoursePayment',
        ),

        # 4. Update Enrollment.source choices — remove 'paymob'
        migrations.AlterField(
            model_name='enrollment',
            name='source',
            field=models.CharField(
                choices=[
                    ('enrollment_code', 'Enrollment Code'),
                    ('admin', 'Admin'),
                ],
                max_length=24,
            ),
        ),
    ]