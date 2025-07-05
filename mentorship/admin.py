from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Mentorship, MentorshipGroup, GroupRequest, GroupChat, GroupMessage, MentorRating, Post, Comment
from accounts.models import User
from courses.models import UserProfile
import logging

# إعداد تسجيل الأخطاء
logger = logging.getLogger(__name__)

class BaseModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all data for {self.model.__name__}")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            logger.info(f"User {request.user.username} has role: {profile.role}")
            if profile.role == 'instructor':
                logger.info(f"Filtering data for instructor {request.user.username} in {self.model.__name__}")
                if self.model == Mentorship:
                    filtered_qs = qs.filter(mentor=request.user)
                    logger.info(f"Found {filtered_qs.count()} mentorships for mentor {request.user.username}")
                    return filtered_qs
                elif self.model == MentorshipGroup:
                    filtered_qs = qs.filter(admin=request.user)
                    logger.info(f"Found {filtered_qs.count()} groups for admin {request.user.username}")
                    return filtered_qs
                elif self.model == GroupRequest:
                    return qs.filter(group__admin=request.user)
                elif self.model == GroupChat:
                    return qs.filter(group__admin=request.user)
                elif self.model == GroupMessage:
                    return qs.filter(chat__group__admin=request.user)
                elif self.model == MentorRating:
                    return qs.filter(mentorship__mentor=request.user)
                elif self.model == Post:
                    return qs.filter(author=request.user)
                elif self.model == Comment:
                    return qs.filter(author=request.user)
            else:
                logger.warning(f"User {request.user.username} with role {profile.role} denied access")
                raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                if obj is None:
                    return True
                if self.model == Mentorship:
                    return obj.mentor == request.user
                elif self.model == MentorshipGroup:
                    return obj.admin == request.user
                elif self.model == GroupRequest:
                    return obj.group.admin == request.user
                elif self.model == GroupChat:
                    return obj.group.admin == request.user
                elif self.model == GroupMessage:
                    return obj.chat.group.admin == request.user
                elif self.model == MentorRating:
                    return obj.mentorship.mentor == request.user
                elif self.model == Post:
                    return obj.author == request.user
                elif self.model == Comment:
                    return obj.author == request.user
            return False
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"User {request.user.username} allowed to add {self.model.__name__}")
                return self.model not in [User, UserProfile]
            return False
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            profile = UserProfile.objects.get(user=request.user)
            logger.info(f"User {request.user.username} has view permission: {profile.role == 'instructor'}")
            return profile.role == 'instructor'
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

@admin.register(Mentorship)
class MentorshipAdmin(BaseModelAdmin):
    list_display = ('mentor', 'mentee', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('mentor__username', 'mentee__username')

@admin.register(MentorshipGroup)
class MentorshipGroupAdmin(BaseModelAdmin):
    list_display = ('name', 'admin', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'admin__username')

@admin.register(GroupRequest)
class GroupRequestAdmin(BaseModelAdmin):
    list_display = ('group', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('group__name', 'user__username')

@admin.register(GroupChat)
class GroupChatAdmin(BaseModelAdmin):
    list_display = ('group', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('group__name',)

@admin.register(GroupMessage)
class GroupMessageAdmin(BaseModelAdmin):
    list_display = ('chat', 'sender', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('chat__group__name', 'sender__username', 'content')

@admin.register(MentorRating)
class MentorRatingAdmin(BaseModelAdmin):
    list_display = ('mentorship', 'mentee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('mentorship__mentor__username', 'mentee__username')

@admin.register(Post)
class PostAdmin(BaseModelAdmin):
    list_display = ('author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content')

@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content')