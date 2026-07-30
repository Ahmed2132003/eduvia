"""
groups/views_assignments.py
============================
Part 34 (المرحلة الثانية) — واجهات إنشاء/تسليم/تصحيح الواجبات (موديلات
GroupAssignment / GroupAssignmentSubmission من Part 33) داخل الجروب.

قرار تنظيمي (نفس نمط views_lessons.py من Part 28 وviews_schedule.py من
Part 32): الـ views دي في ملف منفصل عن groups/views.py الكبير، بدل ما
تتضاف جواه. الـ helpers المشتركة (instructor_required، student_required،
_get_owned_group_or_403، _get_group_and_membership_or_403) اتستوردت من
groups/views.py بدل ما تتكرر — مصدر حقيقة واحد لكل فحص صلاحية.

نفس أسلوب باقي المشروع: function-based views + render + templates، مفيش
class-based views، ومفيش Django Form/ModelForm جديد — قراءة request.POST
يدويًا (نفس نمط create_live_session/upload_group_lesson).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from .models import GroupAssignment, GroupAssignmentSubmission, GroupMembership, TeacherGroup
from .tasks import _notify_student_assignment_graded
from .views import (
    instructor_required,
    student_required,
    _get_owned_group_or_403,
    _get_group_and_membership_or_403,
)


# ---------------------------------------------------------------------------
# Part 34: إنشاء واجب جديد (المدرس صاحب الجروب بس)
# ---------------------------------------------------------------------------

@instructor_required
def create_group_assignment(request, group_id):
    """
    GET: يعرض فورم إنشاء واجب جديد (عنوان، وصف، مرفق اختياري، ميعاد
         تسليم اختياري، الدرجة القصوى).
    POST: بيتحقق من العنوان (إجباري)، وبيتحقق إن max_grade رقم صحيح
         موجب لو اتبعت (وإلا بيسيب القيمة الافتراضية 100 من الموديل)،
         وبيحفظ due_date لو موجود (نفس أسلوب تحويل datetime-local
         المستخدم في create_live_session/upload_group_lesson).
    """
    group = _get_owned_group_or_403(request, group_id)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        attachment = request.FILES.get('attachment')
        due_date_raw = (request.POST.get('due_date') or '').strip()
        max_grade_raw = (request.POST.get('max_grade') or '').strip()

        errors = []
        if not title:
            errors.append('من فضلك اكتب عنوان الواجب.')

        due_date = None
        if due_date_raw:
            try:
                parsed_due_date = timezone.datetime.fromisoformat(due_date_raw)
            except ValueError:
                errors.append('صيغة ميعاد التسليم مش صحيحة.')
            else:
                if timezone.is_naive(parsed_due_date):
                    parsed_due_date = timezone.make_aware(parsed_due_date)
                due_date = parsed_due_date

        max_grade = 100
        if max_grade_raw:
            try:
                max_grade = int(max_grade_raw)
                if max_grade <= 0:
                    raise ValueError
            except ValueError:
                errors.append('الدرجة القصوى لازم تكون رقم صحيح أكبر من صفر.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'groups/create_group_assignment.html', {
                'group': group,
                'form_data': request.POST,
            })

        GroupAssignment.objects.create(
            group=group,
            title=title,
            description=description,
            attachment=attachment,
            due_date=due_date,
            max_grade=max_grade,
        )
        messages.success(request, 'تم إنشاء الواجب بنجاح.')
        return redirect('groups:group_assignments_list', group_id=group.id)

    return render(request, 'groups/create_group_assignment.html', {
        'group': group,
        'form_data': None,
    })


# ---------------------------------------------------------------------------
# Part 34: قايمة واجبات الجروب (المدرس صاحب الجروب + الطالب العضو)
# ---------------------------------------------------------------------------

@login_required
def group_assignments_list(request, group_id):
    """
    نفس فحص الصلاحية المستخدم في group_lessons_list/group_recordings
    بالظبط — عضوية فعلية أو ownership، وبعدين (للطالب العضو بس) لازم
    الجروب يكون "نشط" وإلا بيترجع لصفحة "جروباتي" برسالة التجميد.

    المدرس صاحب الجروب: بيشوف كل واجبات الجروب، ولكل واحد عدد اللي
    سلّموا فعليًا من إجمالي أعضاء الجروب (submissions_count / عدد
    الأعضاء)، عشان يعرف نسبة التسليم بنظرة واحدة.

    الطالب العضو: بيشوف نفس القايمة، ولكل واجب حالة تسليمه هو بالذات
    (لسه ماسلمش / سلّم وقيد المراجعة / اتصحح وبدرجته).
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    assignments = group.assignments.all()
    total_members = group.memberships.count()

    rows = []
    if is_owner:
        for assignment in assignments:
            rows.append({
                'assignment': assignment,
                'submissions_count': assignment.submissions_count,
                'total_members': total_members,
            })
    else:
        my_submissions = {
            sub.assignment_id: sub
            for sub in GroupAssignmentSubmission.objects.filter(
                assignment__group=group, student=request.user,
            )
        }
        for assignment in assignments:
            rows.append({
                'assignment': assignment,
                'my_submission': my_submissions.get(assignment.id),
            })

    return render(request, 'groups/group_assignments_list.html', {
        'group': group,
        'is_owner': is_owner,
        'rows': rows,
    })


# ---------------------------------------------------------------------------
# Part 34: تسليم/تعديل تسليم الطالب لواجب معين
# ---------------------------------------------------------------------------

@student_required
def submit_group_assignment(request, assignment_id):
    """
    الطالب بس (student_required) — تحقق عضوية صريح + فحص تجميد الجروب
    (نفس نمط join_live_session/watch_group_lesson)، لإن الواجب مش تابع
    مباشرة لموديل بيدعم _get_group_and_membership_or_403 (اللي بيسمح
    كمان للمدرس، وده مش مطلوب هنا — الصفحة دي للطالب المسلّم بس).

    GET: يعرض فورم التسليم — لو فيه تسليم قائم للطالب ده على نفس
         الواجب ولسه مش متصحح (graded_at فاضي)، بيعرض بياناته الحالية
         عشان يقدر يعدّلها (مش ينشئ تسليم تاني، unique_together من
         Part 33 بتمنع ده أصلاً). لو متصحح بالفعل، بيعرض الصفحة للقراءة
         بس (من غير فورم) — الطالب يقدر يشوف درجته وملاحظات المدرس.
    POST: يُمنع تمامًا لو فيه تسليم متصحح بالفعل (graded_at موجود) —
         "الطالب يقدر يعدّل تسليمه لحد ما يتصحح" زي ما اتطلب بالظبط.
         غير كده، get_or_create/update عادي (content و/أو attachment،
         واحد منهم على الأقل لازم يكون موجود).
    """
    assignment = get_object_or_404(
        GroupAssignment.objects.select_related('group', 'group__teacher'),
        id=assignment_id,
    )
    group = assignment.group

    is_member = GroupMembership.objects.filter(
        student=request.user, group=group,
    ).exists()
    if not is_member:
        raise PermissionDenied('إنت مش عضو في الجروب ده.')

    if not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    submission = GroupAssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user,
    ).first()

    if submission and submission.is_graded:
        # الواجب اتصحح بالفعل — عرض بس، مفيش فورم تعديل.
        return render(request, 'groups/submit_group_assignment.html', {
            'group': group,
            'assignment': assignment,
            'submission': submission,
            'locked': True,
        })

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        attachment = request.FILES.get('attachment')

        if not content and not attachment and not (submission and submission.attachment):
            messages.error(request, 'اكتب إجابتك أو ارفق ملف قبل التسليم.')
            return render(request, 'groups/submit_group_assignment.html', {
                'group': group,
                'assignment': assignment,
                'submission': submission,
                'locked': False,
            })

        if submission is None:
            submission = GroupAssignmentSubmission(
                assignment=assignment, student=request.user,
            )
        submission.content = content
        if attachment:
            submission.attachment = attachment
        submission.save()

        messages.success(request, 'تم تسليم الواجب بنجاح.')
        return redirect('groups:group_assignments_list', group_id=group.id)

    return render(request, 'groups/submit_group_assignment.html', {
        'group': group,
        'assignment': assignment,
        'submission': submission,
        'locked': False,
    })


# ---------------------------------------------------------------------------
# Part 34: تصحيح تسليمات واجب معين (المدرس صاحب الجروب بس)
# ---------------------------------------------------------------------------

@instructor_required
def grade_submissions(request, assignment_id):
    """
    قايمة كل تسليمات الواجب (المدرس صاحب الجروب بس — نفس فحص ownership
    المستخدم في _get_owned_group_or_403، بس هنا بنفحص على group بتاع
    assignment.group مباشرة لإن الـ URL بياخد assignment_id مش group_id).

    POST: بياخد submission_id + grade + feedback، يتحقق إن الدرجة رقم
    صحيح من 0 لحد max_grade بتاع الواجب، يحدّث التسليم (grade, feedback,
    graded_by=request.user, graded_at=now)، وبيبعت إشعار للطالب (نفس
    نظام Part 16 — send_mail) عن طريق _notify_student_assignment_graded
    من groups/tasks.py.
    """
    assignment = get_object_or_404(
        GroupAssignment.objects.select_related('group', 'group__teacher'),
        id=assignment_id,
    )
    group = assignment.group
    if group.teacher_id != request.user.id:
        raise PermissionDenied('مش مسموحلك توصل للواجب ده.')

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        submission = get_object_or_404(
            GroupAssignmentSubmission, id=submission_id, assignment=assignment,
        )
        grade_raw = (request.POST.get('grade') or '').strip()
        feedback = (request.POST.get('feedback') or '').strip()

        try:
            grade = int(grade_raw)
            if grade < 0 or grade > assignment.max_grade:
                raise ValueError
        except ValueError:
            messages.error(
                request,
                f'الدرجة لازم تكون رقم صحيح من 0 لحد {assignment.max_grade}.',
            )
            return redirect('groups:grade_submissions', assignment_id=assignment.id)

        submission.grade = grade
        submission.feedback = feedback
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save(update_fields=['grade', 'feedback', 'graded_by', 'graded_at'])

        _notify_student_assignment_graded(submission)

        messages.success(request, f'تم تصحيح تسليم {submission.student.username} بنجاح.')
        return redirect('groups:grade_submissions', assignment_id=assignment.id)

    submissions = assignment.submissions.select_related('student').all()

    return render(request, 'groups/grade_submissions.html', {
        'group': group,
        'assignment': assignment,
        'submissions': submissions,
    })