import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0002_groupcapacityplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='groups', to='groups.curriculumcategory')),
                ('current_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups', to='groups.groupcapacityplan')),
                ('teacher', models.ForeignKey(limit_choices_to={'role': 'instructor'}, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('teacher', 'category')},
            },
        ),
    ]