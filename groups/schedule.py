"""
groups/schedule.py
===================
Part 32 (المرحلة الثانية) — تجميع "الجدول القادم" لجروب معين: كل
GroupLiveSession بحالة 'scheduled' وكل GroupLesson مجدولة (is_published
=False وليها publish_at)، في قايمة واحدة مرتبة بالتاريخ (الأقرب أول).

قرار معماري: منطق التجميع/الترتيب ده اتحط في ملف مستقل بسيط (checker/
builder function بنفس روح groups/access.py) بدل ما يتكرر جوه كل view
محتاجاه — الدالة دي مستخدمة من 3 أماكن:
  1) groups/views_schedule.py::group_schedule — صفحة الجدول الكاملة
     لجروب واحد.
  2) groups/views.py::my_learning_groups — ودجت "الجدول القادم" المجمّع
     من كل جروبات الطالب (Part 32، نقطة 3).
  3) groups/views.py::teacher_groups_dashboard — نفس الودجت بس مجمّع من
     كل جروبات المدرس (Part 32، نقطة 4).

عناصر من غير ميعاد فعلي (publish_at=None على الدرس، أو scheduled_at=None
على جلسة اللايف) بيتم استبعادها بالكامل من القايمة — مفيش معنى لعرض
عنصر "قادم" في قايمة مرتبة بالتاريخ من غير تاريخ فعلي نقدر نرتب بيه.
"""


def get_group_schedule_items(group):
    """
    يرجع list من dicts، كل واحد فيه:
      - 'kind': 'live' أو 'lesson'
      - 'title': عنوان الجلسة/الدرس
      - 'when': datetime الميعاد (scheduled_at أو publish_at)
      - 'obj': الكائن نفسه (GroupLiveSession أو GroupLesson)

    مرتبة تصاعديًا بـ 'when' (الأقرب ميعادًا أول).
    """
    items = []

    live_sessions = group.group_live_sessions.filter(
        status='scheduled', scheduled_at__isnull=False,
    )
    for session in live_sessions:
        items.append({
            'kind': 'live',
            'title': session.title,
            'when': session.scheduled_at,
            'obj': session,
        })

    lessons = group.lessons.filter(
        is_published=False, publish_at__isnull=False,
    )
    for lesson in lessons:
        items.append({
            'kind': 'lesson',
            'title': lesson.title,
            'when': lesson.publish_at,
            'obj': lesson,
        })

    items.sort(key=lambda item: item['when'])
    return items