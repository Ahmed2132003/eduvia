from django.contrib import admin
from django.utils import timezone
from django.db import models  # استيراد django.db.models لاستخدام models.Q
from .models import Skill, Service, ServiceOrder, Opportunity, OpportunityApplication, Message
from courses.admin import BaseModelAdmin  # استيراد BaseModelAdmin من courses
from courses.models import UserProfile
from django.core.exceptions import PermissionDenied
import logging

# إعداد تسجيل الأخطاء
logger = logging.getLogger(__name__)

# إجراء جماعي لقبول طلبات الخدمة
def accept_service_orders(modeladmin, request, queryset):
    for order in queryset:
        if order.status == 'pending':
            order.status = 'accepted'
            order.save()
            logger.info(f"Service order {order.id} accepted by {request.user.username}")
    modeladmin.message_user(request, "تم قبول طلبات الخدمة المحددة بنجاح.")
accept_service_orders.short_description = "قبول طلبات الخدمة المحددة"

# إجراء جماعي لقبول طلبات الفرص
def accept_opportunity_applications(modeladmin, request, queryset):
    for application in queryset:
        if application.status == 'pending':
            application.status = 'accepted'
            application.save()
            logger.info(f"Opportunity application {application.id} accepted by {request.user.username}")
    modeladmin.message_user(request, "تم قبول طلبات الفرص المحددة بنجاح.")
accept_opportunity_applications.short_description = "قبول طلبات الفرص المحددة"

@admin.register(Skill)
class SkillAdmin(BaseModelAdmin):
    list_display = ('name', 'user', 'level', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('name', 'user__username')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all skills")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering skills for instructor {request.user.username}")
                return qs.filter(user=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(Service)
class ServiceAdmin(BaseModelAdmin):
    list_display = ('title', 'provider', 'skill', 'price_coins', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'provider__username', 'skill__name')
    list_editable = ('is_active',)
    raw_id_fields = ('provider', 'skill')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all services")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering services for instructor {request.user.username}")
                return qs.filter(provider=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(ServiceOrder)
class ServiceOrderAdmin(BaseModelAdmin):
    list_display = ('service', 'buyer', 'status', 'created_at', 'rating')
    list_filter = ('status', 'created_at')
    search_fields = ('service__title', 'buyer__username')
    actions = [accept_service_orders]
    raw_id_fields = ('service', 'buyer')
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if obj.status == 'completed' and not obj.completed_at:
            obj.completed_at = timezone.now()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all service orders")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering service orders for instructor {request.user.username}")
                return qs.filter(service__provider=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(Opportunity)
class OpportunityAdmin(BaseModelAdmin):
    list_display = ('title', 'provider', 'salary', 'is_open', 'created_at')
    list_filter = ('is_open', 'created_at')
    search_fields = ('title', 'provider__username')
    raw_id_fields = ('provider', 'required_skills')
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all opportunities")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering opportunities for instructor {request.user.username}")
                return qs.filter(provider=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(OpportunityApplication)
class OpportunityApplicationAdmin(BaseModelAdmin):
    list_display = ('full_name', 'opportunity', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('full_name', 'opportunity__title', 'applicant__username')
    actions = [accept_opportunity_applications]
    raw_id_fields = ('opportunity', 'applicant')
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if obj.status == 'accepted' and not obj.order:
            # إنشاء طلب خدمة تلقائي عند قبول طلب الفرصة (اختياري)
            pass
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all opportunity applications")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering opportunity applications for instructor {request.user.username}")
                return qs.filter(opportunity__provider=request.user)
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()

@admin.register(Message)
class MessageAdmin(BaseModelAdmin):
    list_display = ('sender', 'content_preview', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('sender__username', 'content')
    raw_id_fields = ('order', 'opportunity_application', 'sender')
    list_per_page = 25

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = "معاينة الرسالة"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessing all messages")
            return qs
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'instructor':
                logger.info(f"Filtering messages for instructor {request.user.username}")
                return qs.filter(
                    models.Q(order__service__provider=request.user) |
                    models.Q(opportunity_application__opportunity__provider=request.user)
                )
            logger.warning(f"User {request.user.username} with role {profile.role} denied access")
            raise PermissionDenied("Students are not allowed to access the admin panel.")
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile not found for user {request.user.username}")
            return qs.none()