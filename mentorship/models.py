from django.db import models
from django.conf import settings

# موديل لعلاقة المرشد والمتدرب
class Mentorship(models.Model):
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentees')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentors')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('mentor', 'mentee')
        indexes = [
            models.Index(fields=['mentor', 'mentee']),
        ]

    def __str__(self):
        return f"{self.mentor.username} mentors {self.mentee.username}"

from django.db import models
from django.conf import settings  # لاستخدام AUTH_USER_MODEL

class MentorshipGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentorship_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)  # حقل لتحديد إذا كان الجروب عام أو لا

    def __str__(self):
        return self.name

# موديل طلب الانضمام للمجموعة
class GroupRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    group = models.ForeignKey(MentorshipGroup, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        indexes = [
            models.Index(fields=['group', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username}'s request to join {self.group.name}"

# موديل الشات الجماعي
class GroupChat(models.Model):
    group = models.OneToOneField(MentorshipGroup, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.group.name}"

# موديل رسائل المجموعة
class GroupMessage(models.Model):
    chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='group_messages/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat.group.name}"

# موديل تقييم المرشد
class MentorRating(models.Model):
    mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, related_name='ratings')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveIntegerField()  # من 1 إلى 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mentorship', 'mentee')
        indexes = [
            models.Index(fields=['mentorship', 'mentee']),
        ]

    def __str__(self):
        return f"Rating {self.rating} for {self.mentorship.mentor.username} by {self.mentee.username}"
    
from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_posts')
    content = models.TextField()
    image_file = models.FileField(upload_to='media/posts/', blank=True, null=True)  # حقل جديد للصورة/الملف
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentorship_liked_posts', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentorship_disliked_posts', blank=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='mentorship_comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_comments_made')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.post}"