from django.contrib import admin
from .models import Skill, Service, ServiceOrder, Opportunity, OpportunityApplication, Message

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'level', 'created_at']
    list_filter = ['level']
    search_fields = ['name', 'user__username']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'price_coins', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'provider__username']

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['service', 'buyer', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['service__title', 'buyer__username']

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'salary', 'address', 'is_open']
    list_filter = ['is_open']
    search_fields = ['title', 'provider__username']

@admin.register(OpportunityApplication)
class OpportunityApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'opportunity', 'status', 'applied_at']
    list_filter = ['status']
    search_fields = ['full_name', 'opportunity__title']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content', 'sent_at']
    search_fields = ['sender__username', 'content']