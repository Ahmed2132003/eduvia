"""
Part 29 (المرحلة الثانية) — إضافة حقل chat_mode على TeacherGroup.

AddField بسيط، default='open' قابل للتطبيق مباشرة على كل الصفوف
الموجودة بالفعل من غير أي RunPython يدوي (كل جروب موجود هيبقى تلقائيًا
بوضع 'open' زي ما كان فعليًا — مفيش أي جروب "مقفول" قبل الجزء ده أصلاً).

⚠️ dependencies بتفترض إن آخر migration في تطبيق groups هي
'0012_grouplesson' (Part 27)، حسب كل التوثيق المتاح في PROGRESS. لو فيه
migration أحدث اتعملت على السيرفر الحقيقي مش موثقة هنا، لازم تراجع رقم
الـ dependency ده يدويًا قبل ما تشغل makemigrations/migrate — نفس تحذير
كل migration مكتوبة يدويًا في المشروع.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0012_grouplesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachergroup',
            name='chat_mode',
            field=models.CharField(
                choices=[('open', 'open'), ('broadcast_only', 'broadcast_only')],
                default='open',
                max_length=20,
            ),
        ),
    ]