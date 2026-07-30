"""
groups/views_schedule.py
=========================
Part 32 (المرحلة الثانية) — صفحة "الجدول القادم" لجروب معين: قايمة واحدة
مرتبة بالتاريخ بتجمع كل اللايفات المجدولة (GroupLiveSession status=
'scheduled') والدروس المجدولة (GroupLesson is_published=False وليها
publish_at) — تفاصيل التجميع نفسه في groups/schedule.py.

قرار تنظيمي (نفس نمط views_lessons.py من Part 28): view واحدة بسيطة في
ملف منفصل عن groups/views.py بدل ما تتضاف جواه (اللي بقى كبير أصلًا) —
مفيش أي تغيير في السلوك أو الأسماء بسبب القرار ده. الـ helper المشترك
(_get_group_and_membership_or_403) اتستورد من groups/views.py بدل ما
يتكرر، بنفس فلسفة views_lessons.py بالظبط.

نفس أسلوب الكود المتبع في باقي groups/views*.py: function-based view +
render + template، من غير أي منطق جديد مش موجود بالفعل في المشروع.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from .models import TeacherGroup
from .schedule import get_group_schedule_items
from .views import _get_group_and_membership_or_403


@login_required
def group_schedule(request, group_id):
    """
    نفس فحص الصلاحية المستخدم في group_lessons_list/group_recordings
    (Part 26/28) بالظبط — عضوية فعلية أو ownership، وبعدين (للطالب
    العضو بس، مش المدرس) لازم الجروب يكون "نشط" (is_group_content_accessible)
    وإلا بيترجع لصفحة "جروباتي" برسالة التجميد المعتادة. المدرس صاحب
    الجروب دايمًا يقدر يفتح صفحة جدوله حتى لو الجروب متجمد (نفس نمط باقي
    صفحات الجروب للمدرس).

    الروابط: عناصر اللايف بتتحول لرابط join_live_session بس للطالب
    العضو (مش المدرس) — لإن join_live_session نفسها محمية بـ
    student_required فقط (نفس القيد الموثق في group_detail.html، Part
    25)، فمفيش داعي نعرض رابط هيترفض على المدرس. عناصر الدرس بتتحول
    لرابط watch_group_lesson بس للمدرس صاحب الجروب (لإنه الوحيد اللي
    يقدر يفتح درس لسه مش منشور — نفس فحص is_published في
    views_lessons.py::watch_group_lesson من Part 28)؛ للطالب العضو
    العنصر بيتعرض كمعلومة بس (هينزل يوم كذا) من غير رابط، لإن الدرس
    أصلًا مش متاح للمشاهدة قبل موعده.
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    schedule_items = get_group_schedule_items(group)

    return render(request, 'groups/group_schedule.html', {
        'group': group,
        'is_owner': is_owner,
        'schedule_items': schedule_items,
    })