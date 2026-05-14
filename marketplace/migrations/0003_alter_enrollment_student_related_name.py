from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0002_marketplace_core_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enrollment",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="marketplace_enrollments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]