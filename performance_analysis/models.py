from django.db import models
from django.conf import settings
from django.utils.timezone import now
import uuid

class UserPerformance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance')
    total_courses = models.PositiveIntegerField(default=0)
    completed_videos = models.PositiveIntegerField(default=0)
    total_coins = models.PositiveIntegerField(default=0)
    avg_viewing_time = models.FloatField(default=0)  # In seconds
    interaction_rate = models.FloatField(default=0)  # In percentage
    strength_areas = models.TextField(blank=True)  # e.g., "Programming, Math"
    weakness_areas = models.TextField(blank=True)  # e.g., "English"
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Performance of {self.user.username}"

class LearningRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    reason = models.TextField()  # e.g., "Recommended to improve English skills"
    recommended_at = models.DateTimeField(auto_now_add=True)
    priority = models.PositiveIntegerField(default=1)  # 1 (High), 2 (Medium), 3 (Low)

    class Meta:
        ordering = ['priority', '-recommended_at']

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.course.title}"

class PerformanceReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_reports')
    report_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    generated_at = models.DateTimeField(auto_now_add=True)
    performance_summary = models.TextField()
    recommendations = models.TextField()
    emailed = models.BooleanField(default=False)

    def __str__(self):
        return f"Report {self.report_id} for {self.user.username}"
    
from django.db import models
from django.conf import settings  

class UserReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    report_id = models.CharField(max_length=36, unique=True)
    report_file = models.FileField(upload_to='reports/')
    generated_at = models.DateTimeField()

    def __str__(self):
        return f"Report {self.report_id} for {self.user.username}"