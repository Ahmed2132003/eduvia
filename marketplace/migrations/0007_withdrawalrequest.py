# Generated migration — adds WithdrawalRequest + tx_type to WalletTransaction

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "marketplace",
            "0006_coursepayment_remove_coursepurchase_course_and_more",
        ),
    ]

    operations = [
        # Add tx_type to WalletTransaction (was removed in 0006, now re-added cleanly)
        migrations.AddField(
            model_name="wallettransaction",
            name="tx_type",
            field=models.CharField(
                choices=[("earning", "Earning"), ("withdrawal", "Withdrawal")],
                default="earning",
                max_length=16,
            ),
        ),
        # New WithdrawalRequest model
        migrations.CreateModel(
            name="WithdrawalRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                ("withdrawal_code", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("note", models.TextField(blank=True)),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="withdrawal_requests",
                        to="marketplace.instructorwallet",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterModelOptions(
            name="withdrawalrequest",
            options={"ordering": ["-created_at"]},
        ),
    ]