import hashlib

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_code_hash(apps, schema_editor):
    EnrollmentCode = apps.get_model("marketplace", "EnrollmentCode")
    if not hasattr(EnrollmentCode, "code"):
        return
    for obj in EnrollmentCode.objects.all().only("id", "code"):
        raw = (obj.code or "").strip().lower().encode("utf-8")
        obj.code_hash = hashlib.sha256(raw).hexdigest()
        obj.save(update_fields=["code_hash"])


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0002_marketplace_core_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollmentcode",
            name="code_hash",
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
        migrations.RunPython(backfill_code_hash, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="enrollmentcode",
            name="code",
        ),
        migrations.RenameField(
            model_name="enrollmentcode",
            old_name="max_usage",
            new_name="max_uses",
        ),
        migrations.AddField(
            model_name="enrollmentcode",
            name="created_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="created_enrollment_codes", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="enrollmentcode",
            name="code_hash",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]