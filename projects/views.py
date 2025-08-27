from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from .models import Project, Task, TaskSubmission, ProjectComment, CollaborationRoom, RoomMessage, RoomFile, RoomTask, JoinRequest, SubmissionComment, SubmissionRating
from .forms import ProjectForm, TaskForm, TaskSubmissionForm, ProjectCommentForm, RoomForm, MessageForm, FileForm, RoomTaskForm, InviteUserForm, SubmissionCommentForm, SubmissionRatingForm
from courses.views import instructor_required
from django.contrib.auth import get_user_model
import re
from courses.models import UserProfile  
User = get_user_model()

def clean_text(text):
    """تنظيف النص من الأحرف غير المدعومة مع دعم الأحرف العربية"""
    if not text or not text.strip():
        return 'default-title'
    text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', text).strip()
    cleaned = text if text else 'default-title'
    slugified = slugify(cleaned, allow_unicode=True)
    return slugified if slugified else 'default-title'
def check_subscription(request, action, project=None, room=None):
    if not request.user.is_authenticated:
        return False, "يجب تسجيل الدخول للوصول إلى هذه الميزة."
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    plan = user_profile.subscription_plan

    # إذا كانت الخطة منتهية أو غير موجودة
    if not plan or (user_profile.subscription_end_date and user_profile.subscription_end_date < now()):  # هنا التعديل
        return False, "اشتراكك منتهي أو غير موجود. الرجاء الترقية إلى خطة مدفوعة."

    # الخطة المجانية
    if plan == "free":
        return False, "يجب الاشتراك في خطة مدفوعة للوصول إلى هذه الميزة. <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"

    # الخطة الأساسية
    if plan == "basic":
        if action == "view_project":
            viewed_projects = request.session.get('viewed_projects', [])
            if project and project.id not in viewed_projects and len(viewed_projects) >= 3:
                return False, "لقد وصلت إلى الحد الأقصى لعدد المشاريع (3). <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"
        elif action == "join_room":
            joined_rooms = CollaborationRoom.objects.filter(members=request.user).count()
            if joined_rooms >= 3:
                return False, "لقد وصلت إلى الحد الأقصى لعدد الغرف (3). <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"
        elif action in ["create_project", "create_room"]:
            return False, "لا يمكنك إنشاء مشروع أو غرفة تعاون في الخطة الأساسية. <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"

    # الخطة الاحترافية
    if plan == "pro":
        if action == "create_project":
            return False, "لا يمكنك إنشاء مشروع في الخطة الاحترافية. <a href='/accounts/subscribe/'>قم بالترقية إلى خطة المدرب</a>"
        elif action == "create_room":
            created_rooms = CollaborationRoom.objects.filter(creator=request.user).count()
            if created_rooms >= 3:
                return False, "لقد وصلت إلى الحد الأقصى لعدد الغرف التي يمكنك إنشاؤها (3). <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"
        elif action == "join_room":
            joined_rooms = CollaborationRoom.objects.filter(members=request.user).count()
            if joined_rooms >= 6:
                return False, "لقد وصلت إلى الحد الأقصى لعدد الغرف (6). <a href='/accounts/subscribe/'>قم بالترقية الآن</a>"

    # الخطة المميزة
    if plan == "premium":
        if action == "create_project":
            return False, "لا يمكنك إنشاء مشروع في الخطة المميزة. <a href='/accounts/subscribe/'>قم بالترقية إلى خطة المدرب</a>"

    # خطة المدرب (مفتوحة بالكامل)
    if plan == "instructor":
        if user_profile.role != "instructor":
            return False, "يجب أن تكون مدربًا لاستخدام ميزات خطة المدرب."
        return True, ""

    return True, ""
# List all projects
def projects_view(request):
    projects = Project.objects.all()
    for project in projects:
        project.slugified_title = slugify(clean_text(project.title), allow_unicode=True) or 'default-title'
    return render(request, 'projects/projects.html', {'projects': projects})

# Project details
def project_details(request, project_id, project_title):
    project = get_object_or_404(Project, id=project_id)
    cleaned_title = clean_text(project.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != project_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:project_details', kwargs={'project_id': project_id, 'project_title': slugified_title})
        )

    # فحص الاشتراك لعرض تفاصيل المشروع
    can_access, message = check_subscription(request, "view_project", project=project)
    if not can_access:
        messages.error(request, message)
        return redirect('projects:project_list')

    # تسجيل المشروع في الجلسة لتتبع المشاريع التي تمت مشاهدتها
    if request.user.is_authenticated and project:
        viewed_projects = request.session.get('viewed_projects', [])
        if project.id not in viewed_projects:
            viewed_projects.append(project.id)
            request.session['viewed_projects'] = viewed_projects[:3]  # نحدد أقصى 3 مشاريع

    tasks = project.tasks.all()
    for task in tasks:
        task.slugified_title = slugify(clean_text(task.title), allow_unicode=True) or 'default-title'
    comments = project.comments.all()
    return render(request, 'projects/project_details.html', {
        'project': project,
        'tasks': tasks,
        'comments': comments,
    })

# Instructor: Add a new project
@login_required
@instructor_required
def add_project(request):
    can_access, message = check_subscription(request, "create_project")
    if not can_access:
        messages.error(request, message)
        return redirect('projects:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.instructor = request.user
            project.save()
            messages.success(request, 'تم إنشاء المشروع بنجاح!')
            return redirect('projects:project_details', project_id=project.id, project_title=slugify(clean_text(project.title), allow_unicode=True) or 'default-title')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ProjectForm()
    return render(request, 'projects/add_project.html', {'form': form})

# Instructor: Add a task to a project
@login_required
@instructor_required
def add_task(request, project_id, project_title):
    project = get_object_or_404(Project, id=project_id)
    cleaned_title = clean_text(project.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != project_title:
        return redirect('projects:add_task', project_id=project_id, project_title=slugified_title)
    
    can_access, message = check_subscription(request, "create_task")
    if not can_access:
        messages.error(request, message)
        return redirect('projects:project_details', project_id=project.id, project_title=slugified_title)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()  # Save ManyToMany relationships
            return redirect('projects:project_details', project_id=project.id, project_title=slugified_title)
    else:
        form = TaskForm()
    
    return render(request, 'projects/add_task.html', {
        'form': form,
        'project': project,
    })

# Student: Join a task
@login_required
def join_task(request, task_id, task_title):
    task = get_object_or_404(Task, id=task_id)
    cleaned_title = clean_text(task.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != task_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:join_task', kwargs={'task_id': task_id, 'task_title': slugified_title})
        )

    can_access, message = check_subscription(request, "join_task")
    if not can_access:
        messages.error(request, message)
        return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')

    if request.user.courses_profile.role != 'student':
        messages.error(request, 'فقط الطلاب يمكنهم الانضمام إلى المهام.')
        return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
    
    if request.user in task.assigned_to.all():
        messages.info(request, 'أنت بالفعل منضم لهذه المهمة.')
        return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
    
    if request.method == 'POST':
        task.assigned_to.add(request.user)
        messages.success(request, 'لقد انضممت للمهمة بنجاح! يمكنك الآن تقديم الحلول وإضافة تعليقات.')
        return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
    
    return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
# Student: Submit a task
@login_required
def submit_task(request, task_id, task_title):
    task = get_object_or_404(Task, id=task_id)
    cleaned_title = clean_text(task.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != task_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:submit_task', kwargs={'task_id': task_id, 'task_title': slugified_title})
        )
    
    if request.user not in task.assigned_to.all():
        messages.error(request, 'أنت غير معين لهذه المهمة.')
        return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
    
    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task
            submission.student = request.user
            submission.save()
            messages.success(request, 'تم تقديم الحل بنجاح!')
            return redirect('projects:project_details', project_id=task.project.id, project_title=slugify(clean_text(task.project.title), allow_unicode=True) or 'default-title')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = TaskSubmissionForm()
    
    return render(request, 'projects/submit_task.html', {'form': form, 'task': task, 'project': task.project})

# Instructor: Approve a task submission
@login_required
@instructor_required
def approve_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    project = submission.task.project
    if submission.task.project.instructor != request.user:
        messages.error(request, 'غير مصرح لك بالموافقة على هذا التقديم.')
        return redirect('projects:project_details', project_id=project.id, project_title=slugify(clean_text(project.title), allow_unicode=True) or 'default-title')
    
    if request.method == 'POST':
        submission.approved = True
        submission.feedback = request.POST.get('feedback', '')
        submission.approved_at = now()
        submission.save()
        submission.task.completed = True
        submission.task.completed_at = now()
        submission.task.save()
        messages.success(request, 'تمت الموافقة على التقديم!')
        return redirect('projects:project_details', project_id=project.id, project_title=slugify(clean_text(project.title), allow_unicode=True) or 'default-title')
    
    return render(request, 'projects/approve_submission.html', {'submission': submission})

# Add a comment to a project
@login_required
def add_project_comment(request, project_id, project_title):
    project = get_object_or_404(Project, id=project_id)
    cleaned_title = clean_text(project.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != project_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:add_project_comment', kwargs={'project_id': project_id, 'project_title': slugified_title})
        )
    
    if request.method == 'POST':
        form = ProjectCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            messages.success(request, 'تم إضافة التعليق!')
            return redirect('projects:project_details', project_id=project.id, project_title=slugified_title)
    else:
        form = ProjectCommentForm()
    return render(request, 'projects/add_comment.html', {'form': form, 'project': project})

# View task submissions
@login_required
def task_submissions(request, task_id, task_title):
    task = get_object_or_404(Task, id=task_id)
    cleaned_title = clean_text(task.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != task_title:
        return redirect('projects:task_submissions', task_id=task_id, task_title=slugified_title)
    
    submissions = task.submissions.all().select_related('student').prefetch_related('comments', 'ratings')
    return render(request, 'projects/task_submissions.html', {
        'task': task,
        'project': task.project,
        'submissions': submissions,
        'comment_form': SubmissionCommentForm(),
        'rating_form': SubmissionRatingForm(),
    })

# Add comment to submission
@login_required
def add_submission_comment(request, submission_id):
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
            return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')
    return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')

# Rate submission
@login_required
def rate_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    task = submission.task
    if request.method == 'POST':
        form = SubmissionRatingForm(request.POST)
        if form.is_valid():
            SubmissionRating.objects.update_or_create(
                submission=submission,
                user=request.user,
                defaults={'rating': form.cleaned_data['rating']}
            )
            messages.success(request, 'تم تقييم الحل بنجاح!')
            return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')
    return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')

# Distinguish submission
@login_required
def distinguish_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    task = submission.task
    if request.user != submission.task.project.instructor:
        messages.error(request, 'فقط منشئ المشروع يمكنه تمييز الحل.')
        return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')
    
    if request.method == 'POST':
        submission.is_distinguished = True
        submission.save()
        messages.success(request, 'تم تمييز الحل بنجاح!')
        return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')
    return redirect('projects:task_submissions', task_id=task.id, task_title=slugify(clean_text(task.title), allow_unicode=True) or 'default-title')

# Create collaboration room
@login_required
def create_room(request):
    can_access, message = check_subscription(request, "create_room")
    if not can_access:
        messages.error(request, message)
        return redirect('projects:room_list')

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.save()
            room.members.add(request.user)
            messages.success(request, 'تم إنشاء الغرفة بنجاح!')
            return redirect('projects:room_detail', room_id=room.id, room_title=slugify(clean_text(room.title), allow_unicode=True) or 'default-title')
    else:
        form = RoomForm()
    return render(request, 'projects/create_room.html', {'form': form})

# Join room
@login_required
def join_room(request, room_id, room_title):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    cleaned_title = clean_text(room.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:join_room', kwargs={'room_id': room_id, 'room_title': slugified_title})
        )

    can_access, message = check_subscription(request, "join_room", room=room)
    if not can_access:
        messages.error(request, message)
        return redirect('projects:room_list')

    if request.user not in room.members.all():
        room.members.add(request.user)
        messages.success(request, 'لقد انضممت للغرفة!')
    return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)

# Room list
def room_list(request):
    rooms = CollaborationRoom.objects.all()
    for room in rooms:
        room.slugified_title = slugify(clean_text(room.title), allow_unicode=True) or 'default-title'
    join_requests = JoinRequest.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'projects/room_list.html', {
        'rooms': rooms,
        'join_requests': join_requests,
    })

# Room details
@login_required
def room_detail(request, room_id, room_title):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    cleaned_title = clean_text(room.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:room_detail', kwargs={'room_id': room_id, 'room_title': slugified_title})
        )
    
    is_member = request.user in room.members.all() or request.user == room.creator
    join_request = JoinRequest.objects.filter(room=room, user=request.user).first() if request.user.is_authenticated else None
    
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
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.room = room
                message.user = request.user
                message.save()
                return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)
        elif 'file_submit' in request.POST:
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                file = file_form.save(commit=False)
                file.room = room
                file.uploaded_by = request.user
                file.save()
                return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)
        elif 'task_submit' in request.POST:
            task_form = RoomTaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.room = room
                task.save()
                return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)
    
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

# Request to join room
@login_required
def request_join_room(request, room_id, room_title):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    cleaned_title = clean_text(room.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:request_join_room', kwargs={'room_id': room_id, 'room_title': slugified_title})
        )
    
    if request.user == room.creator or request.user in room.members.all():
        messages.info(request, 'أنت بالفعل عضو في هذه الغرفة.')
        return redirect('projects:room_list')
    
    if JoinRequest.objects.filter(user=request.user, room=room, status__in=['pending', 'rejected']).exists():
        messages.info(request, 'لقد قدمت طلب انضمام لهذه الغرفة مسبقًا.')
        return redirect('projects:room_list')
    
    JoinRequest.objects.create(room=room, user=request.user, status='pending')
    messages.success(request, 'تم إرسال طلب الانضمام بنجاح.')
    return redirect('projects:room_list')

# Manage join requests
@login_required
def manage_join_requests(request, room_id, room_title):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    cleaned_title = clean_text(room.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:manage_join_requests', kwargs={'room_id': room_id, 'room_title': slugified_title})
        )
    
    if request.user != room.creator:
        messages.error(request, 'فقط منشئ الغرفة يمكنه إدارة طلبات الانضمام.')
        return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)
    
    join_requests = room.join_requests.filter(status='pending')
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        join_request = get_object_or_404(JoinRequest, id=request_id, room=room)
        
        if action == 'accept':
            join_request.status = 'accepted'
            join_request.save()
            room.members.add(join_request.user)
            messages.success(request, f'تم قبول {"دعوة" if join_request.is_invitation else "طلب انضمام"} {join_request.user.username}.')
        elif action == 'reject':
            join_request.status = 'rejected'
            join_request.save()
            messages.success(request, f'تم رفض {"دعوة" if join_request.is_invitation else "طلب انضمام"} {join_request.user.username}.')
        return redirect('projects:manage_join_requests', room_id=room.id, room_title=slugified_title)
    
    return render(request, 'projects/manage_join_requests.html', {
        'room': room,
        'join_requests': join_requests,
        'invite_form': InviteUserForm(),
    })

# Invite user to room
@login_required
def invite_user(request, room_id, room_title):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    cleaned_title = clean_text(room.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    
    if slugified_title != room_title:
        return HttpResponsePermanentRedirect(
            reverse('projects:invite_user', kwargs={'room_id': room_id, 'room_title': slugified_title})
        )
    
    if request.user != room.creator:
        messages.error(request, 'فقط منشئ الغرفة يمكنه دعو邀 الأعضاء.')
        return redirect('projects:room_detail', room_id=room.id, room_title=slugified_title)

    if request.method == 'POST':
        form = InviteUserForm(request.POST)
        if form.is_valid():
            invited_user = form.cleaned_data['user']
            if invited_user in room.members.all():
                messages.info(request, f'{invited_user.username} هو بالفعل عضو في الغرفة.')
            else:
                join_request, created = JoinRequest.objects.get_or_create(
                    room=room,
                    user=invited_user,
                    defaults={'status': 'pending', 'is_invitation': True}
                )
                if created:
                    messages.success(request, f'تم إرسال دعوة إلى {invited_user.username}.')
                else:
                    messages.info(request, f'تم إرسال دعوة إلى {invited_user.username} مسبقًا.')
            return redirect('projects:manage_join_requests', room_id=room.id, room_title=slugified_title)
    else:
        form = InviteUserForm()
    
    return render(request, 'projects/invite_user.html', {'form': form, 'room': room})