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
Part 21 — badges ملوّنة لحالة الاشتراك في لوحة الأدمن + صفحة رفض منسّقة.
Part 22 — تسجيل GroupLiveSession (المرحلة الثانية: البث المباشر).
Part 27 — تسجيل GroupLesson (المرحلة الثانية: الدروس المسجلة).
Part 29 — إضافة chat_mode لـ TeacherGroupAdmin (list_display + list_filter)
          (المرحلة الثانية: وضع الإذاعة في الشات الجماعي).
Part 33 — تسجيل GroupAssignment و GroupAssignmentSubmission (المرحلة
          الثانية: الواجبات — للمراجعة/الإشراف بس؛ التصحيح الفعلي
          هيتم من view مخصص في Part 34، مش من هنا).
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
    GroupLiveSession,
    GroupLesson,
    GroupAssignment,
    GroupAssignmentSubmission,
    GroupTodoItem,
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
    # Part 22: نفس منطق الألوان اتستخدم لحالات GroupLiveSession كمان
    # (نفس الروح: أخضر = شغال دلوقتي، ذهبي = مجدول لسه، رمادي/وردي = خلص/اتلغى).
    'live': ('#34d399', 'rgba(52,211,153,.12)'),
    'scheduled': ('#fbbf24', 'rgba(251,191,36,.12)'),
    'ended': ('#94a3c4', 'rgba(148,163,196,.12)'),
    'canceled': ('#fb7185', 'rgba(251,113,133,.12)'),
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
    # Part 29 (المرحلة الثانية): chat_mode في list_display + list_filter
    # عشان الأدمن يقدر يشوف/يفلتر الجروبات القافلة شاتها على وضع الإذاعة،
    # نفس نمط باقي الحقول البسيطة في الموديل ده.
    list_display = (
        'name', 'teacher', 'category', 'current_plan', 'is_active',
        'chat_mode', 'join_code', 'created_at',
    )
    list_filter = ('is_active', 'category', 'current_plan', 'chat_mode')
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
    # Part 30: ضفت message_type في list_display/list_filter عشان الأدمن
    # يقدر يميّز بسهولة الرسائل النصية عن الصور/الملفات، وضفت الحقلين
    # الجدد (attachment_image, attachment_file) في readonly_fields بنفس
    # فلسفة باقي الحقول هنا (المراجعة/الإشراف بس، مفيش تعديل من الأدمن).
    list_display = ('group', 'sender', 'message_type', 'short_content', 'sent_at')
    list_filter = ('message_type', 'group__category')
    search_fields = (
        'content',
        'sender__username',
        'sender__email',
        'group__name',
        'group__teacher__username',
    )
    readonly_fields = (
        'group', 'sender', 'message_type', 'content',
        'attachment_image', 'attachment_file', 'sent_at',
    )

    def short_content(self, obj):
        # Part 30: الرسالة ممكن تبقى صورة/ملف من غير أي نص خالص
        # (content فاضي) — بدل ما يظهر فاضي في القايمة، بنعرض وصف
        # مختصر للمرفق نفسه في الحالة دي.
        if obj.content:
            return obj.content if len(obj.content) <= 60 else obj.content[:57] + '...'
        if obj.message_type == 'image' and obj.attachment_image:
            return '📷 صورة'
        if obj.message_type == 'file' and obj.attachment_file:
            return f'📎 {obj.attachment_file_name}'
        return '—'
    short_content.short_description = 'الرسالة'


# ---------------------------------------------------------------------------
# Part 22: تسجيل GroupLiveSession (المرحلة الثانية — البث المباشر).
# نفس نمط التسجيل المتبع في كل موديلات groups (list_display بسيط +
# list_filter + search_fields)، مع badge ملوّن لحالة الجلسة بنفس أسلوب
# _status_badge المستخدم فوق لحالة الاشتراك (Part 21)، عشان الأدمن يقدر
# يتابع الجلسات الشغالة دلوقتي بنظرة واحدة.
# ---------------------------------------------------------------------------

@admin.register(GroupLiveSession)
class GroupLiveSessionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'group',
        'host',
        'mode',
        'status_badge',
        'scheduled_at',
        'started_at',
        'ended_at',
        'created_at',
    )
    list_filter = ('status', 'mode', 'group__category')
    search_fields = (
        'title',
        'group__name',
        'group__teacher__username',
        'host__username',
        'room_identifier',
    )
    # Part 26 (نسخة معدّلة — Manual Recording Upload): recording_url
    # (الحقل القديم بتاع نظام الإيجرس التلقائي) اتشال من الموديل.
    # بدله recording_file (المدرس بيرفعه بنفسه) وrecording_uploaded_at —
    # الاتنين readonly هنا برضه (بيتحدثوا من upload_group_recording view
    # بس، مش من فورم تعديل الأدمن اليدوي).
    readonly_fields = (
        'room_identifier', 'recording_file', 'recording_uploaded_at',
        'started_at', 'ended_at',
    )

    def status_badge(self, obj):
        return _status_badge(obj.status, obj.get_status_display())
    status_badge.short_description = 'الحالة'
    status_badge.admin_order_field = 'status'


# ---------------------------------------------------------------------------
# Part 27: تسجيل GroupLesson (المرحلة الثانية — الدروس المسجلة).
# نفس نمط التسجيل البسيط المتبع في باقي موديلات groups. is_published
# وorder اتحطوا list_editable (نفس أسلوب Part 18 مع
# workshops.LiveRecordingAdmin.is_free_preview) عشان المدرس/الأدمن يقدر
# يرتب الدروس أو ينشر/يخفي درس مباشرة من قايمة الأدمن من غير ما يفتح كل
# سجل لوحده. ضفت action جماعي (toggle_publish) بنفس فلسفة
# toggle_free_preview من Part 18 لتبديل حالة أكتر من درس مختار مرة واحدة.
# ---------------------------------------------------------------------------

@admin.register(GroupLesson)
class GroupLessonAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'group',
        'order',
        'is_published',
        'publish_at',
        'video_duration',
        'created_at',
    )
    list_filter = ('is_published', 'group__category')
    search_fields = (
        'title',
        'description',
        'group__name',
        'group__teacher__username',
    )
    list_editable = ('order', 'is_published')
    actions = ['toggle_publish']

    @admin.action(description='تبديل حالة النشر (منشور/مخفي) للدروس المحددة')
    def toggle_publish(self, request, queryset):
        published_count = 0
        hidden_count = 0
        for lesson in queryset:
            lesson.is_published = not lesson.is_published
            lesson.save(update_fields=['is_published'])
            if lesson.is_published:
                published_count += 1
            else:
                hidden_count += 1

        if published_count:
            self.message_user(
                request,
                f'تم نشر {published_count} درس.',
                level=messages.SUCCESS,
            )
        if hidden_count:
            self.message_user(
                request,
                f'تم إخفاء {hidden_count} درس.',
                level=messages.WARNING,
            )


# ---------------------------------------------------------------------------
# Part 33: تسجيل GroupAssignment و GroupAssignmentSubmission (المرحلة
# الثانية — الواجبات). التسجيل هنا لأغراض المراجعة/الإشراف بس، بنفس
# فلسفة GroupChatMessageAdmin (Part 14) — التصحيح الفعلي (درجة+ملاحظة)
# هيتم من view مخصص للمدرس هيتبنى في Part 34، مش من لوحة الأدمن.
# ---------------------------------------------------------------------------

@admin.register(GroupAssignment)
class GroupAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'group',
        'due_date',
        'max_grade',
        'submissions_count_display',
        'created_at',
    )
    list_filter = ('group__category',)
    search_fields = ('title', 'description', 'group__name', 'group__teacher__username')

    def submissions_count_display(self, obj):
        return obj.submissions_count
    submissions_count_display.short_description = 'عدد التسليمات'


@admin.register(GroupAssignmentSubmission)
class GroupAssignmentSubmissionAdmin(admin.ModelAdmin):
    # كل الحقول readonly هنا (زي GroupChatMessageAdmin من Part 14 بالظبط)
    # — التسليم والتصحيح الفعليين بيتم بالكامل من الواجهة (Part 34)، مش
    # من لوحة الأدمن، فمفيش داعي إن الأدمن "يعدّل" تسليم أو درجة من هنا.
    list_display = (
        'assignment',
        'student',
        'grade_badge',
        'submitted_at',
        'graded_by',
        'graded_at',
    )
    list_filter = ('assignment__group__category',)
    search_fields = (
        'assignment__title',
        'student__username',
        'student__email',
        'assignment__group__name',
        'assignment__group__teacher__username',
    )
    readonly_fields = (
        'assignment', 'student', 'content', 'attachment', 'submitted_at',
        'grade', 'feedback', 'graded_by', 'graded_at',
    )

    def grade_badge(self, obj):
        if obj.grade is None:
            return _status_badge('pending_payment', 'لسه ما اتصححش')
        return _status_badge('active', f'{obj.grade} / {obj.assignment.max_grade}')
    grade_badge.short_description = 'الدرجة'
    grade_badge.admin_order_field = 'grade'


# ---------------------------------------------------------------------------
# Part 35: تسجيل GroupTodoItem (المرحلة الثانية — المهام اليومية). نفس
# نمط التسجيل البسيط المتبع في باقي موديلات groups. is_done اتحطت
# list_editable (نفس فلسفة GroupLessonAdmin.is_published من Part 27)
# عشان الأدمن يقدر يعلّم مهمة "تمت" مباشرة من قايمة الأدمن من غير ما يفتح
# كل سجل لوحده — الاستخدام الفعلي اليومي (تحديد "تم") بيتم من my_todo_list
# (AJAX) مش من هنا، ده بس تسهيل إضافي للمراجعة/الإشراف.
# ---------------------------------------------------------------------------

# Part 36: ضفنا reminder_sent في list_display/list_filter (بنفس فلسفة
# إضافة chat_mode/message_type في أجزاء سابقة) عشان الأدمن يقدر يراجع
# بسهولة أي مهام اتبعتلها تذكير بالفعل ولسه معلّقة.
@admin.register(GroupTodoItem)
class GroupTodoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'group', 'due_at', 'is_done', 'reminder_sent', 'created_at')
    list_filter = ('is_done', 'reminder_sent', 'group__category')
    search_fields = ('title', 'notes', 'owner__username', 'group__name')
    list_editable = ('is_done',)