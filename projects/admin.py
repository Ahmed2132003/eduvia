from django.contrib import admin
from django.utils import timezone
from .models import Project, Task, TaskSubmission, ProjectComment, SubmissionComment, SubmissionRating, CollaborationRoom, RoomMessage, RoomFile, RoomTask, JoinRequest
from courses.admin import BaseModelAdmin  # استيراد BaseModelAdmin من courses
from courses.models import UserProfile
from django.core.exceptions import PermissionDenied
import logging

# إعداد تسجيل الأخطاء
logger = logging.getLogger(__name__)

# إجراء جماعي للموافقة على تقديمات المهام
def approve_submissions(modeladmin, request, queryset):
    for submission in queryset:
        if not submission.approved:
            submission.approved = True
            submission.approved_at = timezone.now()
            submission.feedback = "تمت الموافقة بواسطة الإدارة"
            submission.save()
            submission.task.completed = True
            submission.task.completed_at = timezone.now()
            submission.task.save()
    modeladmin.message_user(request, "تمت الموافقة على التقديمات المحددة بنجاح.")
approve_submissions.short_description = "الموافقة على التقديمات المحددة"

@admin.register(Project)
class ProjectAdmin(BaseModelAdmin):
    list_display = ('title', 'instructor', 'status', 'category', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')  # البحث باستخدام instructor__username
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('instructor',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('tasks')
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all projects")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering projects for instructor {request.user.username}")
                filtered_qs = qs.filter(instructor=request.user)  # ForeignKey
                logger.info(f"Found {filtered_qs.count()} projects for instructor {request.user.username}")
                return filtered_qs
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(Task)
class TaskAdmin(BaseModelAdmin):
    list_display = ('title', 'project', 'priority', 'completed', 'due_date', 'xp_reward', 'coins_reward')
    list_filter = ('priority', 'completed', 'due_date', 'project__status')
    search_fields = ('title', 'description', 'project__title')
    list_editable = ('priority', 'completed', 'xp_reward', 'coins_reward')
    raw_id_fields = ('project', 'assigned_to')
    list_per_page = 25

    def get_assigned_to(self, obj):
        return ", ".join([user.username for user in obj.assigned_to.all()])
    get_assigned_to.short_description = "الطلاب المعينون"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all tasks")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering tasks for instructor {request.user.username}")
                return qs.filter(project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(BaseModelAdmin):
    list_display = ('task', 'student', 'submitted_at', 'approved', 'approved_at')
    list_filter = ('approved', 'submitted_at', 'approved_at')
    search_fields = ('task__title', 'student__username', 'description')
    actions = [approve_submissions]
    raw_id_fields = ('task', 'student')
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if obj.approved and not obj.approved_at:
            obj.approved_at = timezone.now()
            obj.task.completed = True
            obj.task.completed_at = timezone.now()
            obj.task.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all task submissions")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering task submissions for instructor {request.user.username}")
                return qs.filter(task__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(ProjectComment)
class ProjectCommentAdmin(BaseModelAdmin):
    list_display = ('project', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__title', 'user__username', 'content')
    raw_id_fields = ('project', 'user')
    list_per_page = 25

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = "معاينة التعليق"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all project comments")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering project comments for instructor {request.user.username}")
                return qs.filter(project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(SubmissionComment)
class SubmissionCommentAdmin(BaseModelAdmin):
    list_display = ('submission', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('submission__task__title', 'user__username', 'content')
    raw_id_fields = ('submission', 'user')
    list_per_page = 25

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = "معاينة التعليق"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all submission comments")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering submission comments for instructor {request.user.username}")
                return qs.filter(submission__task__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(SubmissionRating)
class SubmissionRatingAdmin(BaseModelAdmin):
    list_display = ('submission', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('submission__task__title', 'user__username')
    raw_id_fields = ('submission', 'user')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all submission ratings")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering submission ratings for instructor {request.user.username}")
                return qs.filter(submission__task__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(CollaborationRoom)
class CollaborationRoomAdmin(BaseModelAdmin):
    list_display = ('title', 'project', 'creator', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'project__title', 'creator__username')
    raw_id_fields = ('project', 'creator', 'members')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all collaboration rooms")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering collaboration rooms for instructor {request.user.username}")
                return qs.filter(project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(RoomMessage)
class RoomMessageAdmin(BaseModelAdmin):
    list_display = ('room', 'user', 'content_preview', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('room__title', 'user__username', 'content')
    raw_id_fields = ('room', 'user')
    list_per_page = 25

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = "معاينة الرسالة"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all room messages")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering room messages for instructor {request.user.username}")
                return qs.filter(room__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(RoomFile)
class RoomFileAdmin(BaseModelAdmin):
    list_display = ('room', 'uploaded_by', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('room__title', 'uploaded_by__username', 'file')
    raw_id_fields = ('room', 'uploaded_by')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all room files")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering room files for instructor {request.user.username}")
                return qs.filter(room__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(RoomTask)
class RoomTaskAdmin(BaseModelAdmin):
    list_display = ('title', 'room', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'room__title', 'description')
    raw_id_fields = ('room', 'assigned_to')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all room tasks")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering room tasks for instructor {request.user.username}")
                return qs.filter(room__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(JoinRequest)
class JoinRequestAdmin(BaseModelAdmin):
    list_display = ('room', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('room__title', 'user__username')
    raw_id_fields = ('room', 'user')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all join requests")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering join requests for instructor {request.user.username}")
                return qs.filter(room__project__instructor=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()