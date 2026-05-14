from django.db import migrations, models
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('courses', '0008_course_instructor_user_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('action', models.CharField(max_length=128)), ('entity_type', models.CharField(max_length=64)), ('entity_id', models.CharField(max_length=64)), ('metadata', models.JSONField(default=dict)), ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL))],
        ),
        migrations.CreateModel(
            name='CoursePurchase',
            fields=[('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('amount', models.DecimalField(decimal_places=2, max_digits=12)), ('currency', models.CharField(default='EGP', max_length=8)), ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)), ('idempotency_key', models.CharField(max_length=128, unique=True)), ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchases', to='courses.course')), ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='course_purchases', to=settings.AUTH_USER_MODEL))],
        ),
    ]