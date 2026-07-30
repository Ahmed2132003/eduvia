from django.db import migrations, models


DEFAULT_PLAN_SIZES = [50, 100, 150, 200, 250, 300]


def seed_default_plans(apps, schema_editor):
    GroupCapacityPlan = apps.get_model('groups', 'GroupCapacityPlan')
    for size in DEFAULT_PLAN_SIZES:
        GroupCapacityPlan.objects.get_or_create(
            max_students=size,
            defaults={'monthly_price': 0.00, 'is_active': True},
        )


def remove_default_plans(apps, schema_editor):
    GroupCapacityPlan = apps.get_model('groups', 'GroupCapacityPlan')
    GroupCapacityPlan.objects.filter(max_students__in=DEFAULT_PLAN_SIZES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupCapacityPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_students', models.PositiveIntegerField()),
                ('monthly_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['max_students'],
            },
        ),
        migrations.RunPython(seed_default_plans, remove_default_plans),
    ]