from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
from .utils import generate_unicode_slug, unique_model_slug
import uuid
import re
from django.utils.timezone import now


def clean_text(text):
    """تنظيف النص من الأحرف غير المدعومة"""
    if not text:
        return 'default'
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return text if text else 'default'


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

    def can_enroll_in_course(self): return True
    def can_view_video(self, course, video_order): return True
    def can_upload_file(self): return True
    def can_view_files(self): return True
    def can_download_certificate(self): return True
    def can_add_course(self): return True
    def can_add_video(self, course): return True
    def can_edit_or_delete(self): return True


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
    instructor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='instructed_courses'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='programming')
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(default=0)
    image = models.URLField(max_length=500, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    total_lessons = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=500, unique=True, allow_unicode=True, blank=True)

    def __str__(self):
        return self.title

    def get_image_url(self):
        return self.image if self.image else 'https://via.placeholder.com/300x200?text=No+Image'

    def get_slug(self):
        if self.slug:
            return self.slug
        return generate_unicode_slug(self.title, fallback_prefix='course', fallback_id=self.id)

    def get_enroll_url(self):
        return reverse('courses:enroll_course', kwargs={
            'course_id': self.id, 'course_slug': self.get_slug()
        })

    def save(self, *args, **kwargs):
        super_result = None
        if not self.pk:
            super_result = super().save(*args, **kwargs)
        if not self.slug:
            self.slug = unique_model_slug(
                Course, self.title,
                fallback_prefix='course', fallback_id=self.pk, instance_pk=self.pk
            )
            super_result = super().save(update_fields=['slug'])
            return super_result
        return super_result or super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:course_details', kwargs={
            'course_id': self.id, 'course_slug': self.get_slug()
        })

    # ── Curriculum helpers ───────────────────────────────────────────────────

    def get_curriculum(self):
        """Return sections with prefetched lessons — single optimized query."""
        return self.sections.prefetch_related('lessons').order_by('order')

    def get_total_lessons_count(self):
        from django.db.models import Count
        result = self.sections.aggregate(total=Count('lessons'))
        return result['total'] or 0

    def get_total_duration(self):
        """Total duration in minutes across all video lessons."""
        from django.db.models import Sum
        result = Lesson.objects.filter(
            section__course=self, lesson_type='video'
        ).aggregate(total=Sum('video_duration'))
        return result['total'] or 0


class CourseEnrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    def is_course_completed(self):
        progress = VideoProgress.objects.filter(user=self.user, video__course=self.course)
        videos = self.course.videos.all()
        return (
            videos.exists()
            and progress.count() == videos.count()
            and all(p.completed for p in progress)
        )


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates'
    )
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='certificates')
    certificate_number = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate {self.certificate_number} for {self.user.username} - {self.course.title}"


class Video(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    description = models.TextField()
    order = models.IntegerField()
    duration = models.FloatField(
        default=10,
        help_text="Duration of the video in minutes (to be entered manually by the instructor)"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.video_url:
            raise ValidationError("يجب إدخال رابط الفيديو.")

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('courses:watch_video', kwargs={
            'course_id': self.course.id,
            'course_slug': self.course.get_slug(),
            'video_id': self.id,
            'video_slug': generate_unicode_slug(self.title, fallback_prefix='video', fallback_id=self.id)
        })


class VideoProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_progress'
    )
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0)
    current_time = models.FloatField(default=0.0, help_text="Current time in seconds")

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"Progress of {self.user.username} in {self.video.title}"

    def get_current_progress(self):
        return self.progress_percentage


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='comments')
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
    file = models.FileField(upload_to='video_files/', null=True, blank=True)
    file_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_instructor_upload = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.file.name or self.file_url} uploaded by {self.user} for {self.video}"


class Task(models.Model):
    video = models.ForeignKey(Video, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Task")
    questions = models.JSONField(
        default=list,
        help_text="List of questions as dictionaries with 'question', 'options', and 'correct_answer'"
    )
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    submitted_answers = models.JSONField(default=list)
    is_correct = models.JSONField(default=list)
    attempt_number = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'task', 'attempt_number')


# ═══════════════════════════════════════════════════════════════════════════════
# NEW CURRICULUM MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Section(models.Model):
    """
    A Section (Module) inside a Course.
    Example: "Section 1 — Introduction to Python"
    """
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='sections',
    )
    title = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.course.title}] Section {self.order}: {self.title}"

    def get_lessons_count(self):
        return self.lessons.count()

    def get_duration(self):
        """Total minutes for video lessons in this section."""
        from django.db.models import Sum
        result = self.lessons.filter(lesson_type='video').aggregate(
            total=Sum('video_duration')
        )
        return result['total'] or 0


class Lesson(models.Model):
    """
    A Lesson inside a Section.
    Can be: Video | Text | Article
    """
    LESSON_TYPE_CHOICES = [
        ('video', 'Video Lesson'),
        ('text', 'Text Lesson'),
        ('article', 'Article'),
    ]

    section = models.ForeignKey(
        'Section',
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    title = models.CharField(max_length=300)
    lesson_type = models.CharField(
        max_length=20,
        choices=LESSON_TYPE_CHOICES,
        default='video',
    )
    order = models.PositiveIntegerField(default=0)

    # ── Video fields ──────────────────────────────────────────────────────────
    video_url = models.URLField(max_length=500, blank=True, null=True)
    video_duration = models.FloatField(
        default=0,
        help_text='Duration in minutes',
    )
    is_preview = models.BooleanField(
        default=False,
        help_text='Free preview — visible before enrollment',
    )

    # ── Text / Article fields ──────────────────────────────────────────────────
    content = models.TextField(blank=True)  # Rich text / HTML content

    # ── Shared ────────────────────────────────────────────────────────────────
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.section.title}] Lesson {self.order}: {self.title}"

    def get_icon(self):
        icons = {
            'video': 'fas fa-play-circle',
            'text': 'fas fa-file-alt',
            'article': 'fas fa-newspaper',
        }
        return icons.get(self.lesson_type, 'fas fa-file')

    def get_type_label(self):
        labels = {
            'video': 'Video',
            'text': 'Text',
            'article': 'Article',
        }
        return labels.get(self.lesson_type, 'Lesson')

    def get_duration_display(self):
        if self.lesson_type == 'video' and self.video_duration:
            mins = int(self.video_duration)
            secs = int((self.video_duration - mins) * 60)
            if secs:
                return f"{mins}m {secs}s"
            return f"{mins}m"
        return ''


class LessonProgress(models.Model):
    """Tracks a student's progress on a Lesson."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='progress',
    )
    completed = models.BooleanField(default=False)
    current_time = models.FloatField(default=0.0)
    progress_percentage = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} — {self.lesson.title} ({self.progress_percentage:.0f}%)"


# ── Signal ────────────────────────────────────────────────────────────────────

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
