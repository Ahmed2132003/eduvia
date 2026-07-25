"""
groups/access.py
=================
Part 15 — تجميد الاشتراكات المنتهية تلقائيًا.

بنفس روح core/access.py الموجود في المشروع: دالة فحص بسيطة (checker
function) بترجع True/False بناءً على حالة فعلية في الداتابيز، من غير أي
اعتماد على request أو session — عشان تتقدر تتستخدم من أي مكان (views،
celery tasks، إلخ) بنفس الطريقة.
"""

from django.utils import timezone

GROUP_FROZEN_MESSAGE = (
    'الجروب متجمد حاليًا، المدرس لسه ما جددش الاشتراك.'
)


def is_group_content_accessible(group) -> bool:
    """
    يرجع True لو فيه GroupSubscription بحالة 'active' لسه سارية فعليًا
    (end_date في المستقبل، أو لسه من غير end_date) للجروب ده دلوقتي.

    قرار معماري: مبنعتمدش على TeacherGroup.is_active وحدها كمصدر
    للحقيقة، لأن الحقل ده بيتحدّث بس في لحظتين (قبول الأدمن في Part
    9/10، والـ celery task الدوري في الجزء ده) ومش بيتحسب لايف. لو حصل
    أي خطأ في تشغيل الـ task الدوري (تأخير، فشل مؤقت، إلخ)، الفلاج ممكن
    يفضل True لجروب اشتراكه خلص فعليًا، أو العكس. فبدل الاعتماد على
    الفلاج، الدالة دي بتتأكد مباشرة من وجود اشتراك 'active' سارٍ فعليًا
    في نفس اللحظة، وده هو مصدر الحقيقة الوحيد لكل الأماكن في المشروع
    (groups/views.py، workshops/views.py، وأي مكان تاني هيحتاج الفحص ده
    مستقبلًا).
    """
    if group is None:
        return False

    return group.subscriptions.filter(status='active').exclude(
        end_date__lt=timezone.now(),
    ).exists()