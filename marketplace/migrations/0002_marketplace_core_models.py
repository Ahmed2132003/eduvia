from decimal import Decimal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source', models.CharField(choices=[('payment', 'Payment'), ('code', 'Enrollment Code'), ('admin', 'Admin')], max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='marketplace_enrollments', to='courses.course')),
                ('purchase', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollment', to='marketplace.coursepurchase')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='marketplace_enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('student', 'course'), name='uq_marketplace_enrollment')],
            },
        ),
        migrations.CreateModel(
            name='EnrollmentCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=64, unique=True)),
                ('expires_at', models.DateTimeField()),
                ('max_usage', models.PositiveIntegerField(default=1)),
                ('used_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='enrollment_codes', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='InstructorWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pending_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('available_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('withdrawn_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('instructor', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='wallet', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.CharField(choices=[('paymob', 'Paymob')], default='paymob', max_length=20)),
                ('provider_order_id', models.CharField(max_length=128, unique=True)),
                ('status', models.CharField(choices=[('initiated', 'Initiated'), ('authorized', 'Authorized'), ('captured', 'Captured'), ('failed', 'Failed')], default='initiated', max_length=20)),
                ('purchase', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='payment', to='marketplace.coursepurchase')),
            ],
        ),
        migrations.CreateModel(
            name='RevenueShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gross_revenue', models.DecimalField(decimal_places=2, max_digits=12)),
                ('platform_fee', models.DecimalField(decimal_places=2, max_digits=12)),
                ('instructor_earnings', models.DecimalField(decimal_places=2, max_digits=12)),
                ('purchase', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='revenue_share', to='marketplace.coursepurchase')),
            ],
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tx_type', models.CharField(choices=[('revenue', 'Revenue'), ('release', 'Release'), ('withdraw', 'Withdraw')], max_length=16)),
                ('reference', models.CharField(max_length=128)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='marketplace.instructorwallet')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('collection_code', models.CharField(max_length=64)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='withdrawal_requests', to='marketplace.instructorwallet')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider_txn_id', models.CharField(max_length=128, unique=True)),
                ('raw_payload', models.JSONField(default=dict)),
                ('signature_valid', models.BooleanField(default=False)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='marketplace.payment')),
            ],
        ),
        migrations.CreateModel(
            name='PayoutApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='approved_payouts', to=settings.AUTH_USER_MODEL)),
                ('withdrawal_request', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='approval', to='marketplace.withdrawalrequest')),
            ],
        ),
    ]