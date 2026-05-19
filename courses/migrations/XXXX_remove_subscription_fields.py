# courses/migrations/XXXX_remove_subscription_fields.py
# ==========================================================
# Migration لإزالة حقول الاشتراكات من UserProfile.
# اسم الملف: ضعه كـ 0002_remove_subscription_fields.py
# أو الرقم التالي لآخر migration موجود في courses.
#
# قبل التطبيق: تأكد أن الحقول التالية موجودة في UserProfile:
#   - subscription_plan
#   - subscription_start_date
#   - subscription_end_date
#   - is_premium  (إن وُجد)
# إذا لم تكن موجودة، احذف العملية المناسبة من operations.
# ==========================================================

from django.db import migrations


class Migration(migrations.Migration):

    # غيِّر هذا إلى اسم آخر migration في تطبيق courses
    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        # أزِل كل حقل من حقول الاشتراك الموجودة في UserProfile
        # احذف أي سطر لا يتوافق مع الحقول الموجودة فعلًا في نموذجك

        migrations.RemoveField(
            model_name='userprofile',
            name='subscription_plan',
        ),

        # أزِل هذا إذا لم يكن الحقل موجودًا:
        # migrations.RemoveField(
        #     model_name='userprofile',
        #     name='subscription_start_date',
        # ),

        # أزِل هذا إذا لم يكن الحقل موجودًا:
        # migrations.RemoveField(
        #     model_name='userprofile',
        #     name='subscription_end_date',
        # ),

        # أزِل هذا إذا لم يكن الحقل موجودًا:
        # migrations.RemoveField(
        #     model_name='userprofile',
        #     name='is_premium',
        # ),
    ]