# courses/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid  

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_profile'
    )
    coins = models.PositiveIntegerField(default=300)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username}'s profile"

    def add_coins(self, amount):
        self.coins += amount
        self.save()

    def deduct_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            self.save()
            return True
        return False

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('programming', 'programming'),
        ('english', 'english'),
        ('math', 'math'),
    ]
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='programming')
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(default=0)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')  
    total_lessons = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

class CourseEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    certificate_issued = models.BooleanField(default=False)  # حقل لتتبع إصدار الشهادة

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    def is_course_completed(self):
        """التحقق مما إذا تم إكمال جميع فيديوهات الكورس"""
        progress = VideoProgress.objects.filter(user=self.user, video__course=self.course)
        videos = self.course.videos.all()
        return videos.exists() and progress.count() == videos.count() and all(p.completed for p in progress)

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='certificates')
    certificate_number = models.CharField(max_length=36, unique=True, default=uuid.uuid4)  # رقم اعتماد فريد
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate {self.certificate_number} for {self.user.username} - {self.course.title}"
import subprocess
from django.db import models
from django.core.exceptions import ValidationError

class Video(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_url = models.URLField()  # حقل إلزامي للرابط
    description = models.TextField()
    order = models.IntegerField()
    unlocked = models.BooleanField(default=False)
    duration = models.FloatField(
        default=10,
        help_text="Duration of the video in minutes (to be entered manually by the instructor)"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def clean(self):
        """التأكد من وجود رابط فيديو"""
        from django.core.exceptions import ValidationError
        if not self.video_url:
            raise ValidationError("يجب إدخال رابط الفيديو.")
    

class VideoProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0)  # نسبة التقدم في الفيديو
    current_time = models.FloatField(default=0.0, help_text="Current time in seconds")

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"Progress of {self.user.username} in {self.video.title}"

    def get_current_progress(self):
        return self.progress_percentage

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    video = models.ForeignKey(
        'Video',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.video}"

class VideoRating(models.Model):
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('video', 'user')

class CourseRating(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('course', 'user')

class VideoFile(models.Model):
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='files')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/video_files/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_instructor_upload = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.file.name} uploaded by {self.user} for {self.video}"

# Signal to create UserProfile automatically when a User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Task(models.Model):
    video = models.ForeignKey(Video, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Task")  # عنوان التاسك
    questions = models.JSONField(default=list, help_text="List of questions as dictionaries with 'question', 'options', and 'correct_answer'")  
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class AlternativeQuiz(models.Model):
    video = models.ForeignKey(Video, related_name='alternative_quizzes', on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=255)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.question

class UserTaskSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    submitted_answers = models.JSONField(default=list) 
    is_correct = models.JSONField(default=list)  
    attempt_number = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'task', 'attempt_number')