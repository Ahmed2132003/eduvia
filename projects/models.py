from django.db import models
from django.conf import settings
import uuid
from django.urls import reverse

class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        limit_choices_to={'courses_profile__role': 'instructor'}
    )
    repository_url = models.URLField(blank=True, null=True)  # e.g., GitHub repo link
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=50, choices=[
        ('web_dev', 'Web Development'),
        ('mobile_dev', 'Mobile Development'),
        ('ai_ml', 'AI/ML'),
        ('other', 'Other'),
    ], default='other')
    image = models.ImageField(upload_to='media/project_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_url = models.URLField(blank=True, null=True)  # Link to GitHub issue
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        blank=True,
        limit_choices_to={'courses_profile__role': 'student'}
    )
    xp_reward = models.PositiveIntegerField(default=100)  # XP for task completion
    coins_reward = models.PositiveIntegerField(default=50)  # Coins for task completion
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"

from django.db import models
from django.conf import settings
from django.db.models import Avg

class TaskSubmission(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_submissions',
        limit_choices_to={'courses_profile__role': 'student'}
    )
    submission_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='media/task_submissions/', blank=True, null=True)
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    is_distinguished = models.BooleanField(default=False)  # حقل التميز

    def __str__(self):
        return f"Submission by {self.student.username} for {self.task.title}"

    def average_rating(self):
        """حساب متوسط التقييم"""
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"
    

class SubmissionComment(models.Model):
    submission = models.ForeignKey(TaskSubmission, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submission_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.submission.task.title}"

class SubmissionRating(models.Model):
    submission = models.ForeignKey(TaskSubmission, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submission_ratings')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # تقييم من 1 إلى 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('submission', 'user')  # منع التقييم المتكرر من نفس المستخدم

    def __str__(self):
        return f"Rating {self.rating} by {self.user.username} for {self.submission.task.title}"
    
    
from django.db import models
from django.conf import settings  # استيراد settings لاستخدام AUTH_USER_MODEL


class CollaborationRoom(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='rooms')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_rooms'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='collaboration_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('projects:room_detail', args=[self.id])

    def __str__(self):
        return self.title

class RoomMessage(models.Model):
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} in {self.room.title}"

class RoomFile(models.Model):
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='room_files/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.file.name} in {self.room.title}"

class RoomTask(models.Model):
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    status = models.CharField(
        max_length=20, 
        choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')],
        default='todo'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task {self.title} in {self.room.title}"

class JoinRequest(models.Model):
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Join request by {self.user.username} for {self.room.title}"