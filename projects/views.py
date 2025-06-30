from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Project, Task, TaskSubmission, ProjectComment
from .forms import ProjectForm, TaskForm, TaskSubmissionForm, ProjectCommentForm
from courses.views import instructor_required
from django.contrib.auth import get_user_model

User = get_user_model()

# List all projects
def projects_view(request):
    projects = Project.objects.all()
    return render(request, 'projects/projects.html', {'projects': projects})

# Project details
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
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
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.instructor = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('projects:project_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'projects/add_project.html', {'form': form})

# Instructor: Add a task to a project
@login_required
@instructor_required
def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id, instructor=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            task.assigned_to.set(form.cleaned_data['assigned_to'])
            messages.success(request, 'Task added successfully!')
            return redirect('projects:project_details', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()
    return render(request, 'projects/add_task.html', {'form': form, 'project': project})

# Student: Join a task
@login_required
def join_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.courses_profile.role != 'student':
        messages.error(request, 'Only students can join tasks.')
        return redirect('projects:project_details', project_id=task.project.id)
    
    if request.user in task.assigned_to.all():
        messages.info(request, 'You are already joined to this task.')
        return redirect('projects:project_details', project_id=task.project.id)
    
    if request.method == 'POST':
        task.assigned_to.add(request.user)
        messages.success(request, 'You have successfully joined the task! You can now submit solutions and add comments.')
        return redirect('projects:project_details', project_id=task.project.id)
    
    return redirect('projects:project_details', project_id=task.project.id)

# Student: Submit a task
@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user not in task.assigned_to.all():
        messages.error(request, 'You are not assigned to this task.')
        return redirect('projects:project_details', project_id=task.project.id)
    
    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task
            submission.student = request.user
            submission.save()
            messages.success(request, 'Solution submitted successfully!')
            return redirect('projects:project_details', project_id=task.project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskSubmissionForm()
    
    return render(request, 'projects/submit_task.html', {'form': form, 'task': task, 'project': task.project})

# Instructor: Approve a task submission
@login_required
@instructor_required
def approve_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    if submission.task.project.instructor != request.user:
        messages.error(request, 'You are not authorized to approve this submission.')
        return redirect('projects:project_details', project_id=submission.task.project.id)
    if request.method == 'POST':
        submission.approved = True
        submission.feedback = request.POST.get('feedback', '')
        submission.approved_at = now()
        submission.save()
        submission.task.completed = True
        submission.task.completed_at = now()
        submission.task.save()
        messages.success(request, 'Submission approved!')
        return redirect('projects:project_details', project_id=submission.task.project.id)
    return render(request, 'projects/approve_submission.html', {'submission': submission})

# Add a comment to a project
@login_required
def add_project_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('projects:project_details', project_id=project.id)
    else:
        form = ProjectCommentForm()
    return render(request, 'projects/add_comment.html', {'form': form, 'project': project})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, TaskSubmission, SubmissionComment, SubmissionRating
from .forms import SubmissionCommentForm, SubmissionRatingForm

@login_required
def task_submissions(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    submissions = task.submissions.all().select_related('student').prefetch_related('comments', 'ratings')
    return render(request, 'projects/task_submissions.html', {
        'task': task,
        'project': task.project,
        'submissions': submissions,
        'comment_form': SubmissionCommentForm(),
        'rating_form': SubmissionRatingForm(),
    })

@login_required
def add_submission_comment(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    if request.method == 'POST':
        form = SubmissionCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submission = submission
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('projects:task_submissions', task_id=submission.task.id)
    return redirect('projects:task_submissions', task_id=submission.task.id)

@login_required
def rate_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    if request.method == 'POST':
        form = SubmissionRatingForm(request.POST)
        if form.is_valid():
            SubmissionRating.objects.update_or_create(
                submission=submission,
                user=request.user,
                defaults={'rating': form.cleaned_data['rating']}
            )
            messages.success(request, 'Solution rated successfully!')
            return redirect('projects:task_submissions', task_id=submission.task.id)
    return redirect('projects:task_submissions', task_id=submission.task.id)

@login_required
def distinguish_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    if request.user != submission.task.project.instructor:
        messages.error(request, 'Only the instructor who created the task can distinguish the solution.')
        return redirect('projects:task_submissions', task_id=submission.task.id)
    if request.method == 'POST':
        submission.is_distinguished = True
        submission.save()
        messages.success(request, 'Solution distinguished successfully!')
        return redirect('projects:task_submissions', task_id=submission.task.id)
    return redirect('projects:task_submissions', task_id=submission.task.id)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CollaborationRoom, Project, Task, RoomMessage, RoomFile, RoomTask
from .forms import RoomForm, MessageForm, FileForm, RoomTaskForm
from django.contrib import messages

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.save()
            room.members.add(request.user)
            messages.success(request, 'Room created successfully!')
            return redirect(room.get_absolute_url())
    else:
        form = RoomForm()
    return render(request, 'projects/create_room.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollaborationRoom, Project, Task, RoomMessage, RoomFile, RoomTask
from .forms import RoomForm, MessageForm, FileForm, RoomTaskForm


@login_required
def join_room(request, room_id):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    if request.user not in room.members:
        room.members.add(request.user)
        messages.success(request, 'You have joined the room!')
    return redirect(room.get_absolute_url())

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollaborationRoom, Project, Task, RoomMessage, RoomFile, RoomTask, JoinRequest
from .forms import RoomForm, MessageForm, FileForm, RoomTaskForm

def room_list(request):
    rooms = CollaborationRoom.objects.all()
    join_requests = JoinRequest.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'projects/room_list.html', {
        'rooms': rooms,
        'join_requests': join_requests,
    })

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    # السماح للجميع برؤية الغرفة، لكن المحتوى الكامل للأعضاء أو المنشئ فقط
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
                return redirect(room.get_absolute_url())
        elif 'file_submit' in request.POST:
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                file = file_form.save(commit=False)
                file.room = room
                file.uploaded_by = request.user
                file.save()
                return redirect(room.get_absolute_url())
        elif 'task_submit' in request.POST:
            task_form = RoomTaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.room = room
                task.save()
                return redirect(room.get_absolute_url())
    
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
def request_join_room(request, room_id):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    if request.user == room.creator or request.user in room.members.all():
        messages.info(request, 'أنت بالفعل عضو أو منشئ هذه الغرفة.')
        return redirect(room.get_absolute_url())
    
    join_request, created = JoinRequest.objects.get_or_create(
        room=room, user=request.user, defaults={'status': 'pending'}
    )
    if created:
        messages.success(request, 'تم إرسال طلب الانضمام بنجاح!')
    else:
        messages.info(request, 'لقد قمت بإرسال طلب انضمام بالفعل.')
    return redirect(room.get_absolute_url())

@login_required
def manage_join_requests(request, room_id):
    room = get_object_or_404(CollaborationRoom, id=room_id)
    if request.user != room.creator:
        messages.error(request, 'فقط منشئ الغرفة يمكنه إدارة طلبات الانضمام.')
        return redirect(room.get_absolute_url())
    
    join_requests = room.join_requests.filter(status='pending')
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        join_request = get_object_or_404(JoinRequest, id=request_id, room=room)
        
        if action == 'accept':
            join_request.status = 'accepted'
            join_request.save()
            room.members.add(join_request.user)
            messages.success(request, f'تم قبول طلب انضمام {join_request.user.username}.')
        elif action == 'reject':
            join_request.status = 'rejected'
            join_request.save()
            messages.success(request, f'تم رفض طلب انضمام {join_request.user.username}.')
        return redirect('projects:manage_join_requests', room_id=room.id)
    
    return render(request, 'projects/manage_join_requests.html', {
        'room': room,
        'join_requests': join_requests,
    })
