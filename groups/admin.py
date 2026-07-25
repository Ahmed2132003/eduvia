"""
groups/admin.py
================
Part 1-6 — تسجيل الموديلات الأساسية.
Part 9 — actions لمراجعة الأدمن وتفعيل/رفض الاشتراك.
Part 10 — نفس action القبول (accept_payment_action) بقى بيراعي إن الاشتراك
          ممكن يكون ناتج عن طلب ترقية (GroupUpgrade)، فبيحسب end_date حسب
          upgrade_mode المختار بدل ما يطبق دايمًا +30 يوم من دلوقتي.
Part 14 — تسجيل GroupChatMessage (للمراجعة/الإشراف بس؛ الإرسال والعرض
          الفعليين للطلاب/المدرسين بيتم من groups/views.py::group_detail).
"""

from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    CurriculumCategory,
    GroupCapacityPlan,
    TeacherGroup,
    GroupSubscription,
    PaymentProof,
    GroupMembership,
    GroupUpgrade,
    GroupChatMessage,
)


# ---------------------------------------------------------------------------
# Part 21: تمييز بصري لحالة الاشتراك/طلب الدفع في لوحة الأدمن — نفس نظام
# الألوان المستخدم في التمبلتس (emerald=نشط/مقبول، gold=معلّق، rose=منتهي/مرفوض)
# عشان الأدمن يميّز الحالات بنظرة واحدة من غير ما يفتح كل سجل لوحده.
# ---------------------------------------------------------------------------
_STATUS_BADGE_COLORS = {
    'active': ('#34d399', 'rgba(52,211,153,.12)'),
    'pending_payment': ('#fbbf24', 'rgba(251,191,36,.12)'),
    'expired': ('#fb7185', 'rgba(251,113,133,.12)'),
    'rejected': ('#fb7185', 'rgba(251,113,133,.12)'),
}


def _status_badge(status_value, label):
    color, bg = _STATUS_BADGE_COLORS.get(status_value, ('#94a3c4', 'rgba(148,163,196,.12)'))
    return format_html(
        '<span style="display:inline-block;padding:3px 10px;border-radius:99px;'
        'font-size:12px;font-weight:700;color:{};background:{};">{}</span>',
        color, bg, label,
    )


@admin.register(CurriculumCategory)
class CurriculumCategoryAdmin(admin.ModelAdmin):
    list_display = ('country', 'stage', 'grade', 'is_active', 'created_at')
    list_filter = ('country', 'stage', 'is_active')
    search_fields = ('country', 'stage', 'grade')


@admin.register(GroupCapacityPlan)
class GroupCapacityPlanAdmin(admin.ModelAdmin):
    list_display = ('max_students', 'monthly_price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('max_students',)


@admin.register(TeacherGroup)
class TeacherGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'category', 'current_plan', 'is_active', 'join_code', 'created_at')
    list_filter = ('is_active', 'category', 'current_plan')
    search_fields = ('name', 'teacher__username', 'teacher__email', 'join_code')
    readonly_fields = ('join_code',)


@admin.register(GroupSubscription)
class GroupSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('group', 'plan', 'status_badge', 'start_date', 'end_date', 'amount_paid', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('group__name', 'group__teacher__username', 'group__teacher__email')

    def status_badge(self, obj):
        return _status_badge(obj.status, obj.get_status_display())
    status_badge.short_description = 'الحالة'
    status_badge.admin_order_field = 'status'


# ---------------------------------------------------------------------------
# Part 9: مراجعة الأدمن وتفعيل الاشتراك
# ---------------------------------------------------------------------------

@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = (
        'subscription',
        'subscription_status',
        'transaction_reference',
        'submitted_at',
        'reviewed_by',
        'reviewed_at',
    )
    list_filter = ('reviewed_by', 'subscription__status')
    search_fields = (
        'subscription__group__name',
        'subscription__group__teacher__username',
        'transaction_reference',
    )
    # reviewed_by/reviewed_at بيتحددوا بس من خلال الـ actions تحت (accept/reject)،
    # مش من فورم التعديل اليدوي في الأدمن، عشان نضمن إن أي تغيير في حالة
    # المراجعة بيمر دايمًا من نفس منطق select_for_update + transaction.atomic.
    readonly_fields = ('reviewed_by', 'reviewed_at')
    actions = ['accept_payment_action', 'reject_payment_action']

    def subscription_status(self, obj):
        return _status_badge(obj.subscription.status, obj.subscription.get_status_display())
    subscription_status.short_description = 'حالة الاشتراك'
    subscription_status.admin_order_field = 'subscription__status'

    # -----------------------------------------------------------------
    # قبول الدفع — بيتفذ فورًا من غير صفحة وسيطة.
    # -----------------------------------------------------------------
    @admin.action(description='✅ قبول الدفع المحدد وتفعيل الاشتراك')
    def accept_payment_action(self, request, queryset):
        accepted = 0
        skipped = 0

        for proof in queryset.select_related('subscription', 'subscription__group', 'subscription__plan'):
            with transaction.atomic():
                # select_for_update عشان نمنع أي race condition لو فيه أكتر
                # من أدمن بيراجع نفس الاشتراك في نفس اللحظة.
                subscription = (
                    GroupSubscription.objects
                    .select_for_update()
                    .get(pk=proof.subscription_id)
                )

                if subscription.status != 'pending_payment':
                    # الاشتراك اتراجع بالفعل (من أدمن تاني أو قبل كده) —
                    # نتجاهله بدل ما نكرر التفعيل أو نبوظ حالة موجودة.
                    skipped += 1
                    continue

                now = timezone.now()
                group = subscription.group

                # Part 10: لو الاشتراك ده ناتج عن طلب ترقية (GroupUpgrade)،
                # لازم نراعي upgrade_mode المختار بدل ما نطبق دايمًا +30 يوم
                # من دلوقتي زي أي اشتراك عادي (Part 9).
                upgrade = subscription.upgrade_source.select_related(None).first()

                # الاشتراك اللي كان active على نفس الجروب قبل الترقية دي
                # (لو موجود) — هيتحول لـ expired عشان مايفضلش فيه اشتراكين
                # active في نفس الوقت لنفس الجروب.
                old_active_subscription = (
                    GroupSubscription.objects
                    .filter(group=group, status='active')
                    .exclude(pk=subscription.pk)
                    .order_by('-end_date')
                    .first()
                )

                if (
                    upgrade
                    and upgrade.upgrade_mode == 'keep_end_date'
                    and old_active_subscription
                    and old_active_subscription.end_date
                ):
                    # نفس تاريخ الانتهاء القديم — منمدش الدورة، بس بنفعّل
                    # الباقة الجديدة لحد نفس الموعد اللي كان هيخلص فيه أصلاً.
                    subscription.start_date = now
                    subscription.end_date = old_active_subscription.end_date
                else:
                    # سلوك عادي (Part 9) أو upgrade_mode == 'reset_cycle':
                    # دورة شهرية جديدة كاملة من دلوقتي.
                    subscription.start_date = now
                    subscription.end_date = now + timedelta(days=30)

                subscription.status = 'active'
                subscription.save(update_fields=['status', 'start_date', 'end_date'])

                if old_active_subscription:
                    old_active_subscription.status = 'expired'
                    old_active_subscription.save(update_fields=['status'])

                group.is_active = True
                group.current_plan = subscription.plan
                group.save(update_fields=['is_active', 'current_plan'])

                proof.reviewed_by = request.user
                proof.reviewed_at = now
                proof.save(update_fields=['reviewed_by', 'reviewed_at'])

                accepted += 1

        if accepted:
            self.message_user(
                request,
                f'تم قبول {accepted} طلب دفع وتفعيل الاشتراك/الجروب المرتبط.',
                level=messages.SUCCESS,
            )
        if skipped:
            self.message_user(
                request,
                f'اتجاهل {skipped} طلب لأن الاشتراك المرتبط مش في حالة '
                f'"pending_payment" أصلاً (تمت مراجعته بالفعل).',
                level=messages.WARNING,
            )

    # -----------------------------------------------------------------
    # رفض الدفع — بيمر على صفحة وسيطة بتطلب سبب الرفض إجباريًا.
    # -----------------------------------------------------------------
    @admin.action(description='❌ رفض الدفع المحدد (يطلب سبب)')
    def reject_payment_action(self, request, queryset):
        # لو الفورم اتبعت (زرار "تأكيد الرفض" في الصفحة الوسيطة)
        if 'apply' in request.POST:
            review_note = (request.POST.get('review_note') or '').strip()

            if not review_note:
                self.message_user(
                    request,
                    'لازم تكتب سبب الرفض قبل التأكيد — عملية الرفض اتلغت.',
                    level=messages.ERROR,
                )
                return None

            selected_ids = request.POST.getlist(ACTION_CHECKBOX_NAME)
            proofs = (
                PaymentProof.objects
                .filter(pk__in=selected_ids)
                .select_related('subscription')
            )

            rejected = 0
            skipped = 0

            for proof in proofs:
                with transaction.atomic():
                    subscription = (
                        GroupSubscription.objects
                        .select_for_update()
                        .get(pk=proof.subscription_id)
                    )

                    if subscription.status != 'pending_payment':
                        skipped += 1
                        continue

                    subscription.status = 'rejected'
                    subscription.save(update_fields=['status'])

                    proof.reviewed_by = request.user
                    proof.reviewed_at = timezone.now()
                    proof.review_note = review_note
                    proof.save(update_fields=['reviewed_by', 'reviewed_at', 'review_note'])

                    rejected += 1

            if rejected:
                self.message_user(
                    request,
                    f'تم رفض {rejected} طلب دفع.',
                    level=messages.SUCCESS,
                )
            if skipped:
                self.message_user(
                    request,
                    f'اتجاهل {skipped} طلب لأن الاشتراك المرتبط مش في حالة '
                    f'"pending_payment" أصلاً.',
                    level=messages.WARNING,
                )
            return None

        # أول مرة يدوس فيها "رفض الدفع المحدد" من قايمة الـ actions —
        # نعرضله صفحة وسيطة تطلب سبب الرفض قبل أي تنفيذ فعلي.
        context = {
            **self.admin_site.each_context(request),
            'title': 'تأكيد رفض الدفع',
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        }
        return render(
            request,
            'admin/groups/paymentproof/reject_confirmation.html',
            context,
        )


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'joined_at')
    list_filter = ('group__category',)
    search_fields = ('student__username', 'student__email', 'group__name', 'group__teacher__username')


@admin.register(GroupUpgrade)
class GroupUpgradeAdmin(admin.ModelAdmin):
    list_display = ('group', 'old_plan', 'new_plan', 'upgrade_mode', 'price_difference', 'created_at')
    list_filter = ('upgrade_mode',)
    search_fields = ('group__name', 'group__teacher__username', 'group__teacher__email')


# ---------------------------------------------------------------------------
# Part 14: تسجيل شات الجروب للمراجعة/الإشراف من الأدمن فقط. الإرسال
# والعرض الفعليين للمدرس/الطلاب بيتم بالكامل من groups/views.py
# (group_detail) — الأدمن هنا وسيلة مراقبة/إشراف بس.
# ---------------------------------------------------------------------------

@admin.register(GroupChatMessage)
class GroupChatMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'short_content', 'sent_at')
    list_filter = ('group__category',)
    search_fields = (
        'content',
        'sender__username',
        'sender__email',
        'group__name',
        'group__teacher__username',
    )
    readonly_fields = ('group', 'sender', 'content', 'sent_at')

    def short_content(self, obj):
        return obj.content if len(obj.content) <= 60 else obj.content[:57] + '...'
    short_content.short_description = 'الرسالة'