"""
groups/urls.py
==============
Part 7 — لوحة تحكم المدرس + فورم إنشاء جروب.
Part 8 — رفع إثبات الدفع.
Part 10 — ترقية سعة الجروب.
Part 11 — انضمام الطالب لمجتمع المدرس.
Part 12 — لوحة "جروباتي" للطالب + صفحة محتوى الجروب (placeholder).
Part 23 — endpoint فاضي (placeholder) لـ webhook مزود البث (LiveKit)،
          هيتملى فعليًا في Part 26. الـ view نفسه في groups/webhooks.py
          (ملف منفصل عن views.py — تفاصيل القرار في PROGRESS، Part 23).
Part 24 — واجهة المدرس: بدء/جدولة لايف (GroupLiveSession) من صفحة
          الجروب. الـ views دي رجعت جوه views.py نفسها (مش ملف منفصل زي
          webhooks.py في Part 23) — في الجزء ده كان معانا views.py
          الحقيقي فعليًا، فمفيش داعي للعزل الاحترازي اللي كان مطلوب لما
          الملف مكانش متاح.
Part 25 — واجهة الطالب: الانضمام للايف داخل الجروب. مسار واحد جديد
          (join_live_session) بياخد session_id بس (من غير group_id في
          الـ URL نفسه — الـ view بيستنتج الجروب من الجلسة مباشرة)،
          لإن الرابط ده هيتستخدم من أكتر من مكان (group_detail،
          my_learning_groups) وأبسط لو مالوش أي اعتماد على group_id
          صريح في المسار.
Part 26 — مكتبة الفيديوهات المسجلة (VOD). مسارين: group_recordings
          (<int:group_id>/recordings/، محتاجة group_id لإنها قايمة
          مكتبة كاملة لجروب معين) وwatch_group_recording
          (live/<int:session_id>/recording/، بياخد session_id بس، نفس
          فلسفة join_live_session فوق).
Part 26 (نسخة معدّلة — Manual Recording Upload) — بدل التسجيل التلقائي
          (LiveKit Egress)، اتضاف مسار جديد upload_group_recording
          (live/<int:session_id>/recording/upload/) عشان المدرس يرفع
          تسجيل اللايف يدويًا بعد ما الجلسة تخلص. نفس فلسفة session_id
          بس في المسار (مش group_id) زي watch_group_recording/
          join_live_session.
Part 28 (المرحلة الثانية) — واجهات رفع/عرض الدروس المسجلة (GroupLesson من
          Part 27). الـ views دي في ملف منفصل (groups/views_lessons.py) مش
          views.py — تفاصيل السبب في الملف نفسه. تلات مسارات جديدة:
          upload_group_lesson (<int:group_id>/lessons/upload/، بياخد
          group_id لإنها عملية إنشاء داخل جروب معين)، group_lessons_list
          (<int:group_id>/lessons/، قايمة كاملة لجروب معين، بياخد group_id
          لنفس السبب)، وwatch_group_lesson (lessons/<int:lesson_id>/watch/،
          بياخد lesson_id بس — نفس فلسفة watch_group_recording/
          join_live_session في استنتاج الجروب من الكائن نفسه).
Part 29 (المرحلة الثانية) — وضع "الإذاعة" في الشات الجماعي. مسار واحد
          جديد toggle_chat_mode (<int:group_id>/chat/toggle-mode/، POST
          بس، للمدرس صاحب الجروب بس) — بيبدّل TeacherGroup.chat_mode بين
          'open' و'broadcast_only'. مركّب من أكتر من segment فمش هيتعارض
          مع الـ pattern العام '<int:group_id>/' في آخر الملف.
Part 32 (المرحلة الثانية) — صفحة "الجدول القادم" لجروب معين (لايفات
          مجدولة + دروس مجدولة). مسار واحد جديد group_schedule
          (<int:group_id>/schedule/، الـ view في groups/views_schedule.py
          — نفس القرار التنظيمي المتبع في views_lessons.py من Part 28).
Part 35 (المرحلة الثانية) — قائمة "مهامي" (GroupTodoItem)، للمدرس
          والطالب على حد سواء. مسارين جديدين في ملف منفصل
          (groups/views_todo.py، نفس القرار التنظيمي المتبع في
          views_lessons.py/views_schedule.py/views_assignments.py):
          my_todo_list (my-todo/، مسار ثابت زي dashboard/) وtoggle_todo_done
          (todo/<int:todo_id>/toggle/، POST فقط، AJAX).
"""

from django.urls import path

from . import views
from . import views_assignments
from . import views_lessons
from . import views_schedule
from . import views_todo
from . import webhooks

app_name = 'groups'

urlpatterns = [
    path('dashboard/', views.teacher_groups_dashboard, name='teacher_dashboard'),
    path('create/', views.create_group, name='create_group'),
    path('category-options/', views.category_options_json, name='category_options_json'),
    path(
        'subscriptions/<int:subscription_id>/payment-proof/',
        views.submit_payment_proof,
        name='submit_payment_proof',
    ),
    path(
        '<int:group_id>/upgrade/',
        views.upgrade_group,
        name='upgrade_group',
    ),
    path(
        'join/<uuid:code>/',
        views.join_teacher_community,
        name='join_teacher_community',
    ),
    path('my-learning/', views.my_learning_groups, name='my_learning_groups'),
    # Part 23: مسار ثابت (string) زي 'dashboard/'/'join/' — لازم يفضل
    # فوق الـ pattern العام '<int:group_id>/' تحت عشان مايتفسرش بالغلط
    # كـ id رقمي (نفس الملاحظة الموثقة في Part 12 عن ترتيب الـ paths).
    path('live/webhook/', webhooks.live_webhook, name='live_webhook'),
    # Part 24: مسارات البث المباشر الجديد (GroupLiveSession). كلها مركّبة
    # من أكتر من segment (<int:group_id>/live/...) فمش هتتعارض مع الـ
    # pattern العام '<int:group_id>/' تحت حتى لو اتحطت بعده، لكن فضّلت
    # الترتيب الواضح ده للقراءة زي باقي الملف.
    path(
        '<int:group_id>/live/create/',
        views.create_live_session,
        name='create_live_session',
    ),
    path(
        '<int:group_id>/live/<int:session_id>/broadcast/',
        views.live_broadcast,
        name='live_broadcast',
    ),
    path(
        '<int:group_id>/live/<int:session_id>/end/',
        views.end_live_session,
        name='end_live_session',
    ),
    # Part 29 (المرحلة الثانية): تبديل وضع الشات الجماعي (open/broadcast_only)
    # للجروب ده. مركّب من أكتر من segment (<int:group_id>/chat/toggle-mode/)
    # فمش هيتعارض مع الـ pattern العام '<int:group_id>/' تحت.
    path(
        '<int:group_id>/chat/toggle-mode/',
        views.toggle_chat_mode,
        name='toggle_chat_mode',
    ),
    # Part 25: صفحة الطالب لمشاهدة/انتظار لايف معين. مسار مستقل بـ
    # session_id بس (بادئ بـ 'live/' زي 'live/webhook/' فوق — مش هيتفسر
    # كـ '<int:group_id>/' أبدًا لإنه مركّب من أكتر من segment ومش رقم
    # خالص في أول segment).
    path(
        'live/<int:session_id>/watch/',
        views.join_live_session,
        name='join_live_session',
    ),
    # Part 26: مكتبة التسجيلات (VOD). مسار قايمة التسجيلات محتاج group_id
    # (زي '<int:group_id>/upgrade/')، بس مسار مشاهدة تسجيل واحد بياخد
    # session_id بس (زي 'live/<int:session_id>/watch/' فوق) — بادئ بـ
    # 'live/' فمش هيتفسر كـ '<int:group_id>/' العام تحت.
    path(
        '<int:group_id>/recordings/',
        views.group_recordings,
        name='group_recordings',
    ),
    path(
        'live/<int:session_id>/recording/',
        views.watch_group_recording,
        name='watch_group_recording',
    ),
    # Part 26 (نسخة معدّلة — Manual Recording Upload): رفع تسجيل اللايف
    # يدويًا. session_id بس (زي السطر اللي فوق مباشرة) — بادئة بـ 'live/'
    # فمش هتتفسر كـ '<int:group_id>/' العام تحت.
    path(
        'live/<int:session_id>/recording/upload/',
        views.upload_group_recording,
        name='upload_group_recording',
    ),
    # Part 28 (المرحلة الثانية): الدروس المسجلة (GroupLesson). مسارين
    # مركّبين من أكتر من segment (<int:group_id>/lessons/...) مش هيتعارضوا
    # مع '<int:group_id>/' العام تحت حتى لو اتحطوا بعده، ومسار مشاهدة
    # درس واحد (watch_group_lesson) بياخد lesson_id بس — نفس فلسفة
    # watch_group_recording/join_live_session فوق في استنتاج الجروب من
    # الدرس نفسه.
    path(
        '<int:group_id>/lessons/upload/',
        views_lessons.upload_group_lesson,
        name='upload_group_lesson',
    ),
    path(
        '<int:group_id>/lessons/',
        views_lessons.group_lessons_list,
        name='group_lessons_list',
    ),
    path(
        'lessons/<int:lesson_id>/watch/',
        views_lessons.watch_group_lesson,
        name='watch_group_lesson',
    ),
    # Part 32 (المرحلة الثانية): صفحة الجدول القادم لجروب معين — مركّبة من
    # أكتر من segment (<int:group_id>/schedule/) فمش هتتعارض مع الـ
    # pattern العام '<int:group_id>/' تحت حتى لو اتحطت قبله.
    path(
        '<int:group_id>/schedule/',
        views_schedule.group_schedule,
        name='group_schedule',
    ),
    # Part 34 (المرحلة الثانية): الواجبات (GroupAssignment/GroupAssignmentSubmission
    # من Part 33). نفس نمط lessons فوق — create/list محتاجين group_id
    # (عملية إنشاء/قايمة داخل جروب معين)، submit وgrade بياخدوا
    # assignment_id بس (الجروب بيتستنتج من الواجب نفسه، نفس فلسفة
    # watch_group_lesson/watch_group_recording).
    path(
        '<int:group_id>/assignments/create/',
        views_assignments.create_group_assignment,
        name='create_group_assignment',
    ),
    path(
        '<int:group_id>/assignments/',
        views_assignments.group_assignments_list,
        name='group_assignments_list',
    ),
    path(
        'assignments/<int:assignment_id>/submit/',
        views_assignments.submit_group_assignment,
        name='submit_group_assignment',
    ),
    path(
        'assignments/<int:assignment_id>/grade/',
        views_assignments.grade_submissions,
        name='grade_submissions',
    ),
    # Part 35 (المرحلة الثانية): قائمة "مهامي" (GroupTodoItem) — مسار ثابت
    # (string) زي 'dashboard/'/'my-learning/'، فلازم يفضل فوق الـ pattern
    # العام '<int:group_id>/' تحت (نفس ملاحظة الترتيب المتكررة في كل
    # الأجزاء اللي فاتت). toggle_todo_done مركّب من أكتر من segment
    # ('todo/<int:todo_id>/toggle/') فمش هيتعارض حتى لو اتحط بعد الـ
    # pattern العام، لكن فضّلت نفس الترتيب الواضح المتبع في باقي الملف.
    path('my-todo/', views_todo.my_todo_list, name='my_todo_list'),
    path(
        'todo/<int:todo_id>/toggle/',
        views_todo.toggle_todo_done,
        name='toggle_todo_done',
    ),
    # Part 37 (المرحلة الثانية): تاب "الأعضاء" في مركز التنقل الموحّد —
    # قايمة أعضاء الجروب، للمدرس صاحب الجروب بس. مركّب من أكتر من
    # segment (<int:group_id>/members/) فمش هيتعارض مع الـ pattern العام
    # '<int:group_id>/' تحت.
    path(
        '<int:group_id>/members/',
        views.group_members,
        name='group_members',
    ),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
]