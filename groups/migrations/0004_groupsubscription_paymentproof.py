import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0003_teachergroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending_payment', 'pending_payment'),
                        ('active', 'active'),
                        ('expired', 'expired'),
                        ('rejected', 'rejected'),
                    ],
                    default='pending_payment',
                    max_length=20,
                )),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='groups.teachergroup')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='groups.groupcapacityplan')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProof',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_image', models.ImageField(upload_to='payment_proofs/')),
                ('transaction_reference', models.CharField(blank=True, max_length=100)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_note', models.TextField(blank=True)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proofs', to='groups.groupsubscription')),
            ],
        ),
    ]