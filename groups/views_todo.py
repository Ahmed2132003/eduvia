"""
groups/views_todo.py
=====================
Part 35 (المرحلة الثانية) — قائمة To-Do بسيطة للمدرس والطالب
(GroupTodoItem من groups/models.py).

قرار تنظيمي (ملف منفصل عن views.py): نفس القرار المتبع في Part 28/32/34
(views_lessons.py / views_schedule.py / views_assignments.py) — الـ views
الجديدة في ملف مستقل بدل ما تتضاف جوه views.py (اللي بقى كبير أصلاً)،
عشان يفضل views.py قابل للمراجعة بسهولة. الملف ده بيستورد GroupTodoItem
من .models مباشرة، ومحتاجش أي helper من views.py (المهام متاحة لأي
مستخدم مسجّل دخول بغض النظر عن دوره — مدرس أو طالب — فمفيش داعي
لـ instructor_required/student_required هنا).

الصلاحية: login_required بس (بدون فحص role) — المهمة شخصية بالكامل
(owner=request.user)، فأي مستخدم مسجّل دخول (مدرس أو طالب) يقدر يستخدم
الصفحة دي بنفس الطريقة.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import GroupTodoItem


@login_required
def my_todo_list(request):
    """
    GET: بيعرض كل مهام المستخدم الحالي (owner=request.user) مرتبة زي ما
    هو محدد في GroupTodoItem.Meta.ordering (المعلّقة أول حاجة، مرتبة
    بالأقرب ميعادًا).
    POST: فورم إضافة سريع (title إجباري + due_at اختياري) — بينشئ
    GroupTodoItem جديدة (owner=request.user، group=None دايمًا هنا —
    الفورم السريع مالوش اختيار جروب، زي ما اتطلب بالظبط في نص الجزء)
    وبيرجّع لنفس الصفحة (Post/Redirect/Get عادي، بنفس نمط باقي فورمات
    المشروع البسيطة).
    """
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        due_at_raw = (request.POST.get('due_at') or '').strip()

        if not title:
            messages.error(request, 'اكتب عنوان المهمة قبل الإضافة.')
            return redirect('groups:my_todo_list')

        due_at = None
        if due_at_raw:
            try:
                parsed = timezone.datetime.fromisoformat(due_at_raw)
                if timezone.is_naive(parsed):
                    parsed = timezone.make_aware(parsed)
                due_at = parsed
            except ValueError:
                messages.error(request, 'صيغة الميعاد مش صحيحة.')
                return redirect('groups:my_todo_list')

        GroupTodoItem.objects.create(
            owner=request.user,
            title=title,
            due_at=due_at,
        )
        return redirect('groups:my_todo_list')

    todos = GroupTodoItem.objects.filter(owner=request.user).select_related('group')

    now = timezone.now()
    pending_todos = [t for t in todos if not t.is_done]
    done_todos = [t for t in todos if t.is_done]

    return render(request, 'groups/my_todo_list.html', {
        'pending_todos': pending_todos,
        'done_todos': done_todos,
        'now': now,
    })


@login_required
@require_POST
def toggle_todo_done(request, todo_id):
    """
    AJAX endpoint بسيط بيبدّل is_done للمهمة المحددة (بدون إعادة تحميل
    الصفحة، زي ما اتطلب بالظبط). تحقق ownership صارم: المهمة لازم تكون
    بتاعة request.user، وإلا 404 (مش 403 — عشان مش هنسرّب أي معلومة عن
    وجود مهمة بتاعة حد تاني بنفس الـ id، نفس مبدأ عدم الإفصاح المعتاد
    لموارد شخصية بحتة).
    """
    try:
        todo = GroupTodoItem.objects.get(id=todo_id, owner=request.user)
    except GroupTodoItem.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not_found'}, status=404)

    todo.is_done = not todo.is_done
    todo.save(update_fields=['is_done'])

    return JsonResponse({'ok': True, 'is_done': todo.is_done})