from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Skill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Service(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_coins = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    delivery_time_days = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ServiceOrder(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders',null=True, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_orders')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    rating = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    details = models.TextField(blank=True, null=True)
    held_coins = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Order {self.service.title} by {self.buyer.username}"

class Opportunity(models.Model):
    title = models.CharField(max_length=200)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opportunities_created')
    description = models.TextField()
    salary = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])  
    address = models.CharField(max_length=200, blank=True, null=True) 
    required_skills = models.ManyToManyField(Skill, related_name='required_for_opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True) 
    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
class OpportunityApplication(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    cv = models.FileField(upload_to='opportunity_cvs/', blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)  
    email = models.EmailField(blank=True, null=True) 
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunity_applications')

    def __str__(self):
        return f"Application by {self.full_name} for {self.opportunity.title}"


class Message(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    opportunity_application = models.ForeignKey(OpportunityApplication, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='service_messages/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.order:
            return f"Message from {self.sender.username} for Order {self.order.id}"
        elif self.opportunity_application:
            return f"Message from {self.sender.username} for Application {self.opportunity_application.id}"