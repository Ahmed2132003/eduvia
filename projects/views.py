"""
projects/views.py
==================
تم إزالة جميع اعتماديات نظام الاشتراكات والخطط (check_subscription, subscription_plan).
الوصول محمي الآن عبر can_access_projects (كورس نشط آخر 60 يوم).
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
import re

from core.access import can_access_projects, ACCESS_DENIED_MESSAGE
from courses.models import UserProfile
from courses.views import instructor_required

from .forms import (
    FileForm,
    InviteUserForm,
    MessageForm,
    ProjectCommentForm,
    ProjectForm,
    RoomForm,
    RoomTaskForm,
    SubmissionCommentForm,
    SubmissionRatingForm,
    TaskForm,
    TaskSubmissionForm,
)
from .models import (
    CollaborationRoom,
    JoinRequest,
    Project,
    ProjectComment,
    RoomFile,
    RoomMessage,
    RoomTask,
    SubmissionComment,
    SubmissionRating,
    Task,
    TaskSubmission,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_text(text):
    """تنظيف النص من الأحرف غير المدعومة مع دعم الأحرف العربية."""
    if not text or not text.strip():
        return 'default-title'
    text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', text).strip()
    cleaned = text if text else 'default-title'
    slugified = slugify(cleaned, allow_unicode=True)
    return slugified if slugified else 'default-title'


def _slugify(text: str) -> str:
    return slugify(clean_text(text), allow_unicode=True) or 'default-title'


def _access_denied(request):
    """رد موحَّد عند رفض الوصول لغير المؤهلين."""
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": ACCESS_DENIED_MESSAGE}, status=403)
    messages.error(request, ACCESS_DENIED_MESSAGE)
    return redirect('projects:project_list')


# ---------------------------------------------------------------------------
# Project List
# ---------------------------------------------------------------------------

def projects_view(request):
    """عرض قائمة المشاريع - مفتوح للجميع (القراءة فقط)."""
    projects = Project.objects.all()
    for project in projects:
        project.slugified_title = _slugify(project.title)
    return render(request, 'projects/projects.html', {'projects': projects})


# ---------------------------------------------------------------------------
# Project Details
# ---------------------------------------------------------------------------

@login_required
def project_details(request, project_id, project_title):
    """تفاصيل المشروع - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    project = get_object_or_404(Project, id=project_id)
    slugified = _slugify(project.title)

    if slugified != project_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:project_details',
                    kwargs={'project_id': project_id, 'project_title': slugified})
        )

    tasks = project.tasks.all()
    for task in tasks:
        task.slugified_title = _slugify(task.title)
    comments = project.comments.all()
    form = ProjectCommentForm()

    return render(request, 'projects/project_details.html', {
        'project': project,
        'tasks': tasks,
        'comments': comments,
        'form': form,
    })


# ---------------------------------------------------------------------------
# Add Project (Instructor only)
# ---------------------------------------------------------------------------

@login_required
@instructor_required
def add_project(request):
    """إضافة مشروع - للمدرسين الذين لديهم كورس نشط."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.instructor = request.user
            project.save()
            messages.success(request, 'تم إنشاء المشروع بنجاح!')
            return redirect(
                'projects:project_details',
                project_id=project.id,
                project_title=_slugify(project.title),
            )
        messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ProjectForm()

    return render(request, 'projects/add_project.html', {'form': form})


# ---------------------------------------------------------------------------
# Add Task (Instructor only)
# ---------------------------------------------------------------------------

@login_required
@instructor_required
def add_task(request, project_id, project_title):
    """إضافة مهمة لمشروع - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    project = get_object_or_404(Project, id=project_id)
    slugified = _slugify(project.title)

    if slugified != project_title:
        return redirect('projects:add_task', project_id=project_id,
                        project_title=slugified)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            return redirect('projects:project_details',
                            project_id=project.id, project_title=slugified)
    else:
        form = TaskForm()

    return render(request, 'projects/add_task.html', {
        'form': form, 'project': project,
    })


# ---------------------------------------------------------------------------
# Join Task (Student)
# ---------------------------------------------------------------------------

@login_required
def join_task(request, task_id, task_title=None):
    """الانضمام إلى مهمة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    task = get_object_or_404(Task, id=task_id)
    project_slug = _slugify(task.project.title)

    if hasattr(request.user, 'courses_profile') and \
            request.user.courses_profile.role != 'student':
        messages.error(request, 'فقط الطلاب يمكنهم الانضمام إلى المهام.')
        return redirect('projects:project_details',
                        project_id=task.project.id, project_title=project_slug)

    if request.user in task.assigned_to.all():
        messages.info(request, 'أنت بالفعل منضم لهذه المهمة.')
        return redirect('projects:project_details',
                        project_id=task.project.id, project_title=project_slug)

    if request.method == 'POST':
        task.assigned_to.add(request.user)
        messages.success(request, 'لقد انضممت للمهمة بنجاح!')

    return redirect('projects:project_details',
                    project_id=task.project.id, project_title=project_slug)


# ---------------------------------------------------------------------------
# Submit Task (Student)
# ---------------------------------------------------------------------------

@login_required
def submit_task(request, task_id, task_title):
    """تقديم حل لمهمة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    task = get_object_or_404(Task, id=task_id)
    slugified = _slugify(task.title)

    if slugified != task_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:submit_task',
                    kwargs={'task_id': task_id, 'task_title': slugified})
        )

    if request.user not in task.assigned_to.all():
        messages.error(request, 'أنت غير معيَّن لهذه المهمة.')
        return redirect('projects:project_details',
                        project_id=task.project.id,
                        project_title=_slugify(task.project.title))

    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task
            submission.student = request.user
            submission.save()
            messages.success(request, 'تم تقديم الحل بنجاح!')
            return redirect('projects:project_details',
                            project_id=task.project.id,
                            project_title=_slugify(task.project.title))
        messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = TaskSubmissionForm()

    return render(request, 'projects/submit_task.html', {
        'form': form, 'task': task, 'project': task.project,
    })


# ---------------------------------------------------------------------------
# Approve Submission (Instructor)
# ---------------------------------------------------------------------------

@login_required
@instructor_required
def approve_submission(request, submission_id):
    """الموافقة على تقديم - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    submission = get_object_or_404(TaskSubmission, id=submission_id)
    project = submission.task.project

    if project.instructor != request.user:
        messages.error(request, 'غير مصرح لك بالموافقة على هذا التقديم.')
        return redirect('projects:project_details',
                        project_id=project.id,
                        project_title=_slugify(project.title))

    if request.method == 'POST':
        submission.approved = True
        submission.feedback = request.POST.get('feedback', '')
        submission.approved_at = now()
        submission.save()
        submission.task.completed = True
        submission.task.completed_at = now()
        submission.task.save()
        messages.success(request, 'تمت الموافقة على التقديم!')
        return redirect('projects:project_details',
                        project_id=project.id,
                        project_title=_slugify(project.title))

    return render(request, 'projects/approve_submission.html',
                  {'submission': submission})


# ---------------------------------------------------------------------------
# Project Comment
# ---------------------------------------------------------------------------

@login_required
def add_project_comment(request, project_id, project_title):
    """إضافة تعليق على مشروع - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    project = get_object_or_404(Project, id=project_id)
    slugified = _slugify(project.title)

    if slugified != project_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:add_project_comment',
                    kwargs={'project_id': project_id, 'project_title': slugified})
        )

    if request.method == 'POST':
        form = ProjectCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            messages.success(request, 'تم إضافة التعليق!')
            return redirect('projects:project_details',
                            project_id=project.id, project_title=slugified)
    else:
        form = ProjectCommentForm()

    return render(request, 'projects/add_comment.html', {
        'form': form, 'project': project,
    })


# ---------------------------------------------------------------------------
# Task Submissions
# ---------------------------------------------------------------------------

@login_required
def task_submissions(request, task_id, task_title):
    """عرض حلول المهمة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    task = get_object_or_404(Task, id=task_id)
    slugified = _slugify(task.title)

    if slugified != task_title:
        return redirect('projects:task_submissions',
                        task_id=task_id, task_title=slugified)

    submissions = task.submissions.all().select_related(
        'student'
    ).prefetch_related('comments', 'ratings')

    return render(request, 'projects/task_submissions.html', {
        'task': task,
        'project': task.project,
        'submissions': submissions,
        'comment_form': SubmissionCommentForm(),
        'rating_form': SubmissionRatingForm(),
    })


# ---------------------------------------------------------------------------
# Submission Comment & Rating
# ---------------------------------------------------------------------------

@login_required
def add_submission_comment(request, submission_id):
    """إضافة تعليق على حل - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    submission = get_object_or_404(TaskSubmission, id=submission_id)
    task = submission.task

    if request.method == 'POST':
        form = SubmissionCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submission = submission
            comment.user = request.user
            comment.save()
            messages.success(request, 'تم إضافة التعليق بنجاح!')

    return redirect('projects:task_submissions',
                    task_id=task.id, task_title=_slugify(task.title))


@login_required
def rate_submission(request, submission_id):
    """تقييم حل - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    submission = get_object_or_404(TaskSubmission, id=submission_id)
    task = submission.task

    if request.method == 'POST':
        form = SubmissionRatingForm(request.POST)
        if form.is_valid():
            SubmissionRating.objects.update_or_create(
                submission=submission,
                user=request.user,
                defaults={'rating': form.cleaned_data['rating']},
            )
            messages.success(request, 'تم تقييم الحل بنجاح!')

    return redirect('projects:task_submissions',
                    task_id=task.id, task_title=_slugify(task.title))


@login_required
def distinguish_submission(request, submission_id):
    """تمييز حل - للمدرس فقط، يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    submission = get_object_or_404(TaskSubmission, id=submission_id)
    task = submission.task

    if request.user != submission.task.project.instructor:
        messages.error(request, 'فقط منشئ المشروع يمكنه تمييز الحل.')
        return redirect('projects:task_submissions',
                        task_id=task.id, task_title=_slugify(task.title))

    if request.method == 'POST':
        submission.is_distinguished = True
        submission.save()
        messages.success(request, 'تم تمييز الحل بنجاح!')

    return redirect('projects:task_submissions',
                    task_id=task.id, task_title=_slugify(task.title))


# ---------------------------------------------------------------------------
# Collaboration Rooms
# ---------------------------------------------------------------------------

@login_required
def create_room(request):
    """إنشاء غرفة تعاون - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.save()
            room.members.add(request.user)
            messages.success(request, 'تم إنشاء الغرفة بنجاح!')
            return redirect('projects:room_detail',
                            room_id=room.id, room_title=_slugify(room.title))
    else:
        form = RoomForm()

    return render(request, 'projects/create_room.html', {'form': form})


@login_required
def join_room(request, room_id, room_title):
    """الانضمام إلى غرفة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    room = get_object_or_404(CollaborationRoom, id=room_id)
    slugified = _slugify(room.title)

    if slugified != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:join_room',
                    kwargs={'room_id': room_id, 'room_title': slugified})
        )

    if request.user not in room.members.all():
        room.members.add(request.user)
        messages.success(request, 'لقد انضممت للغرفة!')

    return redirect('projects:room_detail', room_id=room.id, room_title=slugified)


def room_list(request):
    """قائمة الغرف - مفتوحة للجميع (القراءة فقط)."""
    rooms = CollaborationRoom.objects.all()
    for room in rooms:
        room.slugified_title = _slugify(room.title)
    join_requests = (
        JoinRequest.objects.filter(user=request.user)
        if request.user.is_authenticated else []
    )
    return render(request, 'projects/room_list.html', {
        'rooms': rooms, 'join_requests': join_requests,
    })


@login_required
def room_detail(request, room_id, room_title):
    """تفاصيل غرفة التعاون - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    room = get_object_or_404(CollaborationRoom, id=room_id)
    slugified = _slugify(room.title)

    if slugified != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:room_detail',
                    kwargs={'room_id': room_id, 'room_title': slugified})
        )

    is_member = request.user in room.members.all() or request.user == room.creator
    join_request = (
        JoinRequest.objects.filter(room=room, user=request.user).first()
        if request.user.is_authenticated else None
    )

    if is_member:
        message_form = MessageForm()
        file_form = FileForm()
        task_form = RoomTaskForm()
        todo_tasks = room.tasks.filter(status='todo')
        in_progress_tasks = room.tasks.filter(status='in_progress')
        done_tasks = room.tasks.filter(status='done')
    else:
        message_form = file_form = task_form = None
        todo_tasks = in_progress_tasks = done_tasks = None

    if request.method == 'POST' and is_member:
        if 'message_submit' in request.POST:
            mf = MessageForm(request.POST)
            if mf.is_valid():
                msg = mf.save(commit=False)
                msg.room = room
                msg.user = request.user
                msg.save()
                return redirect('projects:room_detail',
                                room_id=room.id, room_title=slugified)
        elif 'file_submit' in request.POST:
            ff = FileForm(request.POST, request.FILES)
            if ff.is_valid():
                f = ff.save(commit=False)
                f.room = room
                f.uploaded_by = request.user
                f.save()
                return redirect('projects:room_detail',
                                room_id=room.id, room_title=slugified)
        elif 'task_submit' in request.POST:
            tf = RoomTaskForm(request.POST)
            if tf.is_valid():
                t = tf.save(commit=False)
                t.room = room
                t.save()
                return redirect('projects:room_detail',
                                room_id=room.id, room_title=slugified)

    return render(request, 'projects/room_detail.html', {
        'room': room,
        'is_member': is_member,
        'join_request': join_request,
        'message_form': message_form,
        'file_form': file_form,
        'task_form': task_form,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
    })


@login_required
def request_join_room(request, room_id, room_title=None):
    """طلب الانضمام إلى غرفة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    room = get_object_or_404(CollaborationRoom, id=room_id)
    slugified = _slugify(room.title)

    if room_title and slugified != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:request_join_room',
                    kwargs={'room_id': room_id, 'room_title': slugified})
        )

    if request.user == room.creator or request.user in room.members.all():
        messages.info(request, 'أنت بالفعل عضو في هذه الغرفة.')
        return redirect('projects:room_list')

    if JoinRequest.objects.filter(
        user=request.user, room=room, status__in=['pending', 'rejected']
    ).exists():
        messages.info(request, 'لقد قدمت طلب انضمام لهذه الغرفة مسبقًا.')
        return redirect('projects:room_list')

    JoinRequest.objects.create(room=room, user=request.user, status='pending')
    messages.success(request, 'تم إرسال طلب الانضمام بنجاح.')
    return redirect('projects:room_list')


@login_required
def manage_join_requests(request, room_id, room_title):
    """إدارة طلبات الانضمام - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    room = get_object_or_404(CollaborationRoom, id=room_id)
    slugified = _slugify(room.title)

    if slugified != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:manage_join_requests',
                    kwargs={'room_id': room_id, 'room_title': slugified})
        )

    if request.user != room.creator:
        messages.error(request, 'فقط منشئ الغرفة يمكنه إدارة طلبات الانضمام.')
        return redirect('projects:room_detail', room_id=room.id, room_title=slugified)

    join_requests = room.join_requests.filter(status='pending')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        join_request = get_object_or_404(JoinRequest, id=request_id, room=room)

        if action == 'accept':
            join_request.status = 'accepted'
            join_request.save()
            room.members.add(join_request.user)
            label = 'دعوة' if join_request.is_invitation else 'طلب انضمام'
            messages.success(request, f'تم قبول {label} {join_request.user.username}.')
        elif action == 'reject':
            join_request.status = 'rejected'
            join_request.save()
            label = 'دعوة' if join_request.is_invitation else 'طلب انضمام'
            messages.success(request, f'تم رفض {label} {join_request.user.username}.')

        return redirect('projects:manage_join_requests',
                        room_id=room.id, room_title=slugified)

    return render(request, 'projects/manage_join_requests.html', {
        'room': room,
        'join_requests': join_requests,
        'invite_form': InviteUserForm(),
    })


@login_required
def invite_user(request, room_id, room_title):
    """دعوة مستخدم إلى غرفة - يتطلب كورسًا نشطًا."""
    if not can_access_projects(request.user):
        return _access_denied(request)

    room = get_object_or_404(CollaborationRoom, id=room_id)
    slugified = _slugify(room.title)

    if slugified != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:invite_user',
                    kwargs={'room_id': room_id, 'room_title': slugified})
        )

    if request.user != room.creator:
        messages.error(request, 'فقط منشئ الغرفة يمكنه دعوة الأعضاء.')
        return redirect('projects:room_detail', room_id=room.id, room_title=slugified)

    if request.method == 'POST':
        form = InviteUserForm(request.POST)
        if form.is_valid():
            invited_user = form.cleaned_data['user']
            if invited_user in room.members.all():
                messages.info(request, f'{invited_user.username} هو بالفعل عضو.')
            else:
                _, created = JoinRequest.objects.get_or_create(
                    room=room,
                    user=invited_user,
                    defaults={'status': 'pending', 'is_invitation': True},
                )
                if created:
                    messages.success(request, f'تم إرسال دعوة إلى {invited_user.username}.')
                else:
                    messages.info(request, f'تم إرسال دعوة إلى {invited_user.username} مسبقًا.')
            return redirect('projects:manage_join_requests',
                            room_id=room.id, room_title=slugified)
    else:
        form = InviteUserForm()

    return render(request, 'projects/invite_user.html', {
        'form': form, 'room': room,
    })