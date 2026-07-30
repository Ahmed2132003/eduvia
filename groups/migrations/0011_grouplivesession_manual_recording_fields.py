"""
groups/migrations/0011_grouplivesession_manual_recording_fields.py
====================================================================
Part 26 (نسخة معدّلة — Manual Recording Upload).

⚠️ ملحوظة مهمة زي كل migration مكتوبة يدويًا في المشروع ده (نفس الملاحظة
المتكررة من Part 22/Part 15): الملف ده اتكتب اعتمادًا على إن آخر
migration فعلية في تطبيق groups هي 0010_grouplivesession (Part 22) —
حسب كل التوثيق المتاح في PROGRESS، مفيش أي migration جديدة اتضافت في
Part 23/24/25 (الأجزاء دي كانت views/urls/templates/settings بس، من غير
أي تعديل على models.py). لو فيه migration تانية اتعملت على السيرفر
الحقيقي مش موثقة هنا، لازم تراجع قيمة `dependencies` تحت يدويًا قبل ما
تشغل makemigrations/migrate.

العملية: إزالة recording_url (URLField، كانت مخصصة لنظام Egress
التلقائي الملغي)، وإضافة 3 حقول بديلة لنظام الرفع اليدوي: recording_file
(FileField)، recording_uploaded_at (DateTimeField)، recording_duration
(DurationField). الثلاثة كلها nullable/blank — مفيش أي RunPython مطلوب،
كل الصفوف الموجودة (لو فيها) هتتحول تلقائيًا لقيم فاضية.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0010_grouplivesession'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouplivesession',
            name='recording_url',
        ),
        migrations.AddField(
            model_name='grouplivesession',
            name='recording_file',
            field=models.FileField(
                blank=True, null=True, upload_to='group_live_recordings/',
            ),
        ),
        migrations.AddField(
            model_name='grouplivesession',
            name='recording_uploaded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='grouplivesession',
            name='recording_duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]