from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Profile(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free Plan'),
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('premium', 'Premium Plan'),
        ('instructor', 'Instructor Plan'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    profile_picture = models.URLField(blank=True, null=True)  
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    xp = models.PositiveIntegerField(default=0)  
    coins = models.PositiveIntegerField(default=0)
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    subscription_end_date = models.DateTimeField(blank=True, null=True)  
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)  
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    paymob_order_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_duration = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('six_months', 'Six Months'), ('yearly', 'Yearly')],
        blank=True,
        null=True
    )
    paymob_order_id = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Creating profile for user: {instance.username}")
        Profile.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
        
from django.db import models
from django.conf import settings
# accounts/models.py
class InstructorPayout(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    payout_date = models.DateTimeField(auto_now_add=True)
    course_views = models.PositiveIntegerField(default=0)  
    total_platform_views = models.PositiveIntegerField(default=0)  
    payout_percentage = models.FloatField() 

    def __str__(self):
        return f"Payout of ${self.amount} to {self.instructor.username} on {self.payout_date}"
class UserChat(models.Model):
    # المحادثة بين مستخدمين
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  
        indexes = [
            models.Index(fields=['user1', 'user2']),
        ]

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class UserMessage(models.Model):
    chat = models.ForeignKey(UserChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='user_messages/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in Chat {self.chat.id}"