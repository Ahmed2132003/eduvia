# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from .models import User, Profile, UserChat, UserMessage, InstructorPayout
import logging

logger = logging.getLogger(__name__)


class BaseModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            if request.user.role == 'instructor':
                raise PermissionDenied("Instructors are not allowed to access this model.")
            raise PermissionDenied("Only superusers can access this model.")
        except AttributeError:
            return qs.none()

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return self.has_view_permission(request)


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(BaseModelAdmin):
    list_display = ('user', 'full_name', 'xp', 'coins')
    list_filter = ('user__role',)
    search_fields = ('user__username', 'full_name')
    fieldsets = (
        (None, {'fields': ('user', 'full_name')}),
        ('Details', {'fields': ('profile_picture', 'date_of_birth', 'xp', 'coins')}),
    )


@admin.register(UserChat)
class UserChatAdmin(BaseModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user1__username', 'user2__username')


@admin.register(UserMessage)
class UserMessageAdmin(BaseModelAdmin):
    list_display = ('chat', 'sender', 'content', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('sender__username', 'content')
    readonly_fields = ('sent_at',)


@admin.register(InstructorPayout)
class InstructorPayoutAdmin(BaseModelAdmin):
    list_display = ('instructor', 'amount', 'payout_date', 'course_views', 'total_platform_views', 'payout_percentage')
    list_filter = ('payout_date',)
    search_fields = ('instructor__username',)
    fieldsets = (
        (None, {'fields': ('instructor', 'amount')}),
        ('Payout Details', {'fields': ('payout_date', 'course_views', 'total_platform_views', 'payout_percentage')}),
    )
    readonly_fields = ('payout_date',)
