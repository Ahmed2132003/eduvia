"""
Part 30 (المرحلة الثانية) — إرفاق صور وملفات في الشات الجماعي.

تعديل على GroupChatMessage (من Part 14):
  - content بقى blank=True (رسالة صورة/ملف ممكن متبقاش ليها نص خالص).
  - message_type: CharField جديد (text/image/file)، default='text' —
    كل الرسائل الموجودة بالفعل قبل الجزء ده هتتصنف تلقائيًا 'text' (وهي
    فعليًا كانت كلها نصوص، فده صحيح 100% للبيانات القديمة من غير أي
    RunPython مطلوب).
  - attachment_image / attachment_file: حقلين جدد اختياريين (null/blank)
    — الرسائل القديمة هتفضل من غيرهم عادي.

⚠️ dependencies بتفترض إن آخر migration في تطبيق groups هي
'0013_teachergroup_chat_mode' (Part 29)، حسب الملف اللي بعته Ahmed فعليًا
في نفس الجلسة دي. لو فيه migration أحدث اتعملت على السيرفر الحقيقي مش
موصولة هنا، لازم تراجع رقم الـ dependency ده يدويًا قبل ما تشغل
makemigrations/migrate — نفس تحذير كل migration مكتوبة يدويًا في المشروع.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0013_teachergroup_chat_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupchatmessage',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='groupchatmessage',
            name='message_type',
            field=models.CharField(
                choices=[('text', 'text'), ('image', 'image'), ('file', 'file')],
                default='text',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='groupchatmessage',
            name='attachment_image',
            field=models.ImageField(
                blank=True, null=True, upload_to='group_chat/images/',
            ),
        ),
        migrations.AddField(
            model_name='groupchatmessage',
            name='attachment_file',
            field=models.FileField(
                blank=True, null=True, upload_to='group_chat/files/',
            ),
        ),
    ]