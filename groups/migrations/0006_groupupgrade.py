import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_groupmembership'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupUpgrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upgrade_mode', models.CharField(choices=[('keep_end_date', 'keep_end_date'), ('reset_cycle', 'reset_cycle')], max_length=20)),
                ('price_difference', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upgrades', to='groups.teachergroup')),
                ('new_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='groups.groupcapacityplan')),
                ('old_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='groups.groupcapacityplan')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upgrade_source', to='groups.groupsubscription')),
            ],
        ),
    ]