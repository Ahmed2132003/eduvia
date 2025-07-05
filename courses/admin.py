from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Course, Video, Comment, UserProfile, Task, AlternativeQuiz, UserTaskSubmission, VideoFile, CourseEnrollment, Certificate, VideoProgress, VideoRating, CourseRating
from projects.models import Project, Task as ProjectTask, TaskSubmission, ProjectComment, SubmissionComment, SubmissionRating, CollaborationRoom, RoomMessage, RoomFile, RoomTask, JoinRequest
from skills_market.models import Skill, Service, ServiceOrder, Opportunity, OpportunityApplication, Message
from workshops.models import LiveSession, LiveRecording
import logging

logger = logging.getLogger(__name__)

# إلغاء تسجيل Group و UserProfile إذا كانوا مسجلين
admin.site.unregister(Group)
if UserProfile in admin.site._registry:
    admin.site.unregister(UserProfile)

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
                if self.model == Course:
                    return qs.filter(instructor=request.user.username)
                elif self.model == Video:
                    return qs.filter(course__instructor=request.user.username)
                elif self.model == Comment:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == Task:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == AlternativeQuiz:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == UserTaskSubmission:
                    return qs.filter(task__video__course__instructor=request.user.username)
                elif self.model == VideoFile:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == CourseEnrollment:
                    return qs.filter(course__instructor=request.user.username)
                elif self.model == Certificate:
                    return qs.filter(course__instructor=request.user.username)
                elif self.model == VideoProgress:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == VideoRating:
                    return qs.filter(video__course__instructor=request.user.username)
                elif self.model == CourseRating:
                    return qs.filter(course__instructor=request.user.username)
                elif self.model == Project:
                    return qs.filter(instructor=request.user)
                elif self.model == ProjectTask:
                    return qs.filter(project__instructor=request.user)
                elif self.model == TaskSubmission:
                    return qs.filter(task__project__instructor=request.user)
                elif self.model == ProjectComment:
                    return qs.filter(project__instructor=request.user)
                elif self.model == SubmissionComment:
                    return qs.filter(submission__task__project__instructor=request.user)
                elif self.model == SubmissionRating:
                    return qs.filter(submission__task__project__instructor=request.user)
                elif self.model == CollaborationRoom:
                    return qs.filter(project__instructor=request.user)
                elif self.model == RoomMessage:
                    return qs.filter(room__project__instructor=request.user)
                elif self.model == RoomFile:
                    return qs.filter(room__project__instructor=request.user)
                elif self.model == RoomTask:
                    return qs.filter(room__project__instructor=request.user)
                elif self.model == JoinRequest:
                    return qs.filter(room__project__instructor=request.user)
                elif self.model == Skill:
                    return qs.filter(user=request.user)
                elif self.model == Service:
                    return qs.filter(provider=request.user)
                elif self.model == ServiceOrder:
                    return qs.filter(service__provider=request.user)
                elif self.model == Opportunity:
                    return qs.filter(provider=request.user)
                elif self.model == OpportunityApplication:
                    return qs.filter(opportunity__provider=request.user)
                elif self.model == Message:
                    return qs.filter(
                        models.Q(order__service__provider=request.user) |
                        models.Q(opportunity_application__opportunity__provider=request.user)
                    )
                elif self.model == LiveSession:
                    return qs.filter(instructor=request.user)
                elif self.model == LiveRecording:
                    return qs.filter(live_session__instructor=request.user)
                elif self.model == Group:
                    logger.warning(f"Instructor {request.user.username} denied access to Groups")
                    return qs.none()  # إخفاء Groups من المحاضرين
                elif self.model == UserProfile:
                    logger.warning(f"Instructor {request.user.username} denied access to UserProfile")
                    return qs.none()  # إخفاء UserProfile من المحاضرين
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
                if self.model == Course:
                    return obj.instructor == request.user.username
                elif self.model == Video:
                    return obj.course.instructor == request.user.username
                elif self.model == Comment:
                    return obj.video.course.instructor == request.user.username
                elif self.model == Task:
                    return obj.video.course.instructor == request.user.username
                elif self.model == AlternativeQuiz:
                    return obj.video.course.instructor == request.user.username
                elif self.model == UserTaskSubmission:
                    return obj.task.video.course.instructor == request.user.username
                elif self.model == VideoFile:
                    return obj.video.course.instructor == request.user.username
                elif self.model == CourseEnrollment:
                    return obj.course.instructor == request.user.username
                elif self.model == Certificate:
                    return obj.course.instructor == request.user.username
                elif self.model == VideoProgress:
                    return obj.video.course.instructor == request.user.username
                elif self.model == VideoRating:
                    return obj.video.course.instructor == request.user.username
                elif self.model == CourseRating:
                    return obj.course.instructor == request.user.username
                elif self.model == Project:
                    return obj.instructor == request.user
                elif self.model == ProjectTask:
                    return obj.project.instructor == request.user
                elif self.model == TaskSubmission:
                    return obj.task.project.instructor == request.user
                elif self.model == ProjectComment:
                    return obj.project.instructor == request.user
                elif self.model == SubmissionComment:
                    return obj.submission.task.project.instructor == request.user
                elif self.model == SubmissionRating:
                    return obj.submission.task.project.instructor == request.user
                elif self.model == CollaborationRoom:
                    return obj.project.instructor == request.user
                elif self.model == RoomMessage:
                    return obj.room.project.instructor == request.user
                elif self.model == RoomFile:
                    return obj.room.project.instructor == request.user
                elif self.model == RoomTask:
                    return obj.room.project.instructor == request.user
                elif self.model == JoinRequest:
                    return obj.room.project.instructor == request.user
                elif self.model == Skill:
                    return obj.user == request.user
                elif self.model == Service:
                    return obj.provider == request.user
                elif self.model == ServiceOrder:
                    return obj.service.provider == request.user
                elif self.model == Opportunity:
                    return obj.provider == request.user
                elif self.model == OpportunityApplication:
                    return obj.opportunity.provider == request.user
                elif self.model == Message:
                    return obj.order.service.provider == request.user if obj.order else obj.opportunity_application.opportunity.provider == request.user
                elif self.model == LiveSession:
                    return obj.instructor == request.user
                elif self.model == LiveRecording:
                    return obj.live_session.instructor == request.user
                elif self.model == Group:
                    logger.warning(f"Instructor {request.user.username} denied change permission for Groups")
                    return False  # منع المحاضرين من تعديل Groups
                elif self.model == UserProfile:
                    logger.warning(f"Instructor {request.user.username} denied change permission for UserProfile")
                    return False  # منع المحاضرين من تعديل UserProfile
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
                return self.model not in [User, UserProfile, Group]  # منع المحاضرين من إضافة Groups و UserProfile
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
            if self.model in [UserProfile, Group]:
                logger.warning(f"Instructor {request.user.username} denied view permission for {self.model.__name__}")
                return False  # منع المحاضرين من رؤية UserProfile و Groups
            return profile.role == 'instructor'
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return False

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            profile = UserProfile.objects.get(user=request.user)
            if self.model in [UserProfile, Group]:
                logger.warning(f"Instructor {request.user.username} denied module permission for {self.model.__name__}")
                return False  # منع المحاضرين من رؤية قسم UserProfile و Groups في الإدارة
            return profile.role == 'instructor'
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return False

# إجراءات جماعية لنماذج Courses
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

# تسجيل نماذج Courses
@admin.register(Course)
class CourseAdmin(BaseModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'instructor', 'description')
    list_per_page = 25

@admin.register(Video)
class VideoAdmin(BaseModelAdmin):
    list_display = ('title', 'course', 'order', 'unlocked')
    list_filter = ('course', 'unlocked')
    search_fields = ('title', 'description')
    list_per_page = 25

@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username')
    list_per_page = 25

@admin.register(Task)
class TaskAdmin(BaseModelAdmin):
    list_display = ('title', 'video', 'order')
    list_filter = ('video__course',)
    search_fields = ('title',)
    list_per_page = 25

@admin.register(AlternativeQuiz)
class AlternativeQuizAdmin(BaseModelAdmin):
    list_display = ('question', 'video', 'used')
    list_filter = ('video__course', 'used')
    search_fields = ('question',)
    list_per_page = 25

@admin.register(UserTaskSubmission)
class UserTaskSubmissionAdmin(BaseModelAdmin):
    list_display = ('user', 'task', 'attempt_number', 'submitted_at')
    list_filter = ('task__video__course', 'submitted_at')
    search_fields = ('user__username',)
    actions = [approve_submissions]
    list_per_page = 25

@admin.register(VideoFile)
class VideoFileAdmin(BaseModelAdmin):
    list_display = ('video', 'user', 'uploaded_at', 'is_instructor_upload')
    list_filter = ('video__course', 'uploaded_at', 'is_instructor_upload')
    search_fields = ('user__username', 'description')
    list_per_page = 25

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(BaseModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'certificate_issued')
    list_filter = ('enrolled_at', 'certificate_issued')
    search_fields = ('user__username', 'course__title')
    list_per_page = 25

@admin.register(Certificate)
class CertificateAdmin(BaseModelAdmin):
    list_display = ('certificate_number', 'user', 'course', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('certificate_number', 'user__username', 'course__title')
    list_per_page = 25

@admin.register(VideoProgress)
class VideoProgressAdmin(BaseModelAdmin):
    list_display = ('user', 'video', 'completed', 'progress_percentage')
    list_filter = ('completed',)
    search_fields = ('user__username', 'video__title')
    list_per_page = 25

@admin.register(VideoRating)
class VideoRatingAdmin(BaseModelAdmin):
    list_display = ('video', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'video__title')
    list_per_page = 25

@admin.register(CourseRating)
class CourseRatingAdmin(BaseModelAdmin):
    list_display = ('course', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'course__title')
    list_per_page = 25

# تسجيل نموذج Group
@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 25

# تسجيل نموذج UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(BaseModelAdmin):
    list_display = ('user', 'role', 'coins')
    list_filter = ('role',)
    search_fields = ('user__username',)
    list_per_page = 25