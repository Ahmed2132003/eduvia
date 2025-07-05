from django.contrib import admin
from django.contrib.auth.models import User
from .models import Competition, Question, Participant, Answer, Certificate
from courses.models import UserProfile
from django.core.exceptions import PermissionDenied
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
                if self.model == Competition:
                    filtered_qs = qs.filter(instructor=request.user)
                    logger.info(f"Found {filtered_qs.count()} competitions for instructor {request.user.username}")
                    return filtered_qs
                elif self.model == Question:
                    return qs.filter(competition__instructor=request.user)
                elif self.model == Participant:
                    return qs.filter(competition__instructor=request.user)
                elif self.model == Answer:
                    return qs.filter(question__competition__instructor=request.user)
                elif self.model == Certificate:
                    return qs.filter(competition__instructor=request.user)
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
                if self.model == Competition:
                    return obj.instructor == request.user
                elif self.model == Question:
                    return obj.competition.instructor == request.user
                elif self.model == Participant:
                    return obj.competition.instructor == request.user
                elif self.model == Answer:
                    return obj.question.competition.instructor == request.user
                elif self.model == Certificate:
                    return obj.competition.instructor == request.user
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

# Inline للسماح بتعديل الأسئلة داخل المسابقة
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'choices', 'correct_answer', 'points', 'coins')
    list_display = ('text', 'question_type')

# Inline لعرض المشاركين داخل المسابقة
class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    fields = ('user', 'total_xp', 'total_coins', 'joined_at')
    readonly_fields = ('user', 'total_xp', 'total_coins', 'joined_at')
    can_delete = False

@admin.register(Competition)
class CompetitionAdmin(BaseModelAdmin):
    list_display = ('title', 'instructor', 'start_time', 'end_time', 'is_active', 'is_ongoing')
    list_filter = ('is_active', 'start_time', 'instructor')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_time'
    inlines = [QuestionInline, ParticipantInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'question_time_limit', 'is_active')
        }),
    )

    def is_ongoing(self, obj):
        return obj.is_ongoing
    is_ongoing.boolean = True
    is_ongoing.short_description = 'Ongoing'

@admin.register(Question)
class QuestionAdmin(BaseModelAdmin):
    list_display = ('text', 'competition', 'question_type', 'points', 'coins')
    list_filter = ('competition', 'question_type')
    search_fields = ('text', 'competition__title')
    fieldsets = (
        (None, {
            'fields': ('competition', 'text', 'question_type')
        }),
        ('Answer Details', {
            'fields': ('choices', 'correct_answer', 'points', 'coins')
        }),
    )

@admin.register(Participant)
class ParticipantAdmin(BaseModelAdmin):
    list_display = ('user', 'competition', 'total_xp', 'total_coins', 'joined_at')
    list_filter = ('competition',)
    search_fields = ('user__username', 'competition__title')
    readonly_fields = ('joined_at', 'total_xp', 'total_coins')

@admin.register(Answer)
class AnswerAdmin(BaseModelAdmin):
    list_display = ('participant', 'question', 'answer_text', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'question__competition')
    search_fields = ('participant__user__username', 'question__text', 'answer_text')
    readonly_fields = ('submitted_at', 'is_correct')

@admin.register(Certificate)
class CertificateAdmin(BaseModelAdmin):
    list_display = ('certificate_number', 'user', 'competition', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('certificate_number', 'user__username', 'competition__title')