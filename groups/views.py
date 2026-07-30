"""
groups/views.py
================
Part 7 — لوحة تحكم المدرس + فورم إنشاء جروب.
Part 8 — رفع إثبات الدفع.
Part 10 — ترقية سعة الجروب.
Part 13 — ربط LiveSession بالجروب (تعديل group_detail من Part 12).
Part 14 — شات جماعي داخل الجروب (تعديل تاني على group_detail؛ بدل ما نعمل
          view/URL منفصل للشات، استخدمنا نفس نمط الـ action dispatch اللي
          Part 13 عملته لـ attach/detach_session، وضفنا action='send_message'
          ليه — تفاصيل القرار في PROGRESS.md).
Part 15 — تجميد الاشتراكات المنتهية تلقائيًا: استبدلنا الحساب المحلي
          القديم (_group_is_currently_active) باستخدام
          groups.access.is_group_content_accessible كمصدر حقيقة مركزي
          واحد، مستخدم هنا وفي workshops/views.py. تفاصيل في PROGRESS.md.
Part 24 (المرحلة الثانية) — واجهة المدرس: بدء/جدولة لايف (GroupLiveSession،
          النظام الجديد بـ LiveKit من Part 22/23) من صفحة الجروب. views جديدة:
          create_live_session، live_broadcast، end_live_session. group_detail
          اتعدّلت (إضافة، مش استبدال) عشان تعرض قسم "اللايف المباشر" الجديد —
          منفصل تمامًا عن قسم "جلسات لايف" القديم (workshops.LiveSession من
          Part 13، نظام Google Meet). تفاصيل كاملة في PROGRESS_PART22.md.
Part 25 (المرحلة الثانية) — واجهة الطالب: الانضمام للايف داخل الجروب. view
          جديدة واحدة (join_live_session) بتتفرع حسب status الجلسة
          (scheduled/live/ended/canceled)، بنفس صلاحيات Part 15
          (GroupMembership + is_group_content_accessible). تفاصيل كاملة في
          PROGRESS_PART22.md.
Part 26 (المرحلة الثانية) — مكتبة الفيديوهات المسجلة (VOD). view
          جديدتين: group_recordings (قايمة كل GroupLiveSession المسجلة
          لجروب معين) وwatch_group_recording (صفحة مشاهدة تسجيل واحد).
          join_live_session (Part 25) اتعدّلت (فرع status == 'ended' بس)
          عشان توجّه الطالب فعليًا لصفحة التسجيل الجديدة بدل رسالة
          "هتتاح قريبًا" — تفاصيل كاملة في PROGRESS_PART22.md.
Part 26 (نسخة معدّلة — Manual Recording Upload) — استبدال نظام التسجيل
          التلقائي (LiveKit Egress -> S3) برفع يدوي من المدرس بعد ما
          اللايف يخلص. view جديدة: upload_group_recording. group_recordings
          وwatch_group_recording وjoin_live_session اتعدّلوا يشتغلوا على
          session.recording_file بدل session.recording_url. تفاصيل كاملة
          في PROGRESS (قسم "Part 26 — نسخة معدّلة").
Part 29 (المرحلة الثانية) — وضع "الإذاعة" في الشات الجماعي: حقل جديد
          TeacherGroup.chat_mode ('open'/'broadcast_only'). view جديدة
          toggle_chat_mode (POST بس، للمدرس صاحب الجروب بس). منطق
          send_message جوه group_detail اتعدّل عشان يمنع أي حد غير
          المدرس من الإرسال لو chat_mode == 'broadcast_only'.
Part 34 (المرحلة الثانية) — واجهات الواجبات (views_assignments.py، ملف
          منفصل). التعديل الوحيد هنا: my_learning_groups() بقت بتحسب
          كمان pending_assignments_count لكل جروب نشط (عدد الواجبات
          اللي لسه ملهاش تسليم من الطالب)، عشان my_learning_groups.html
          يعرضه كتنبيه بسيط جنب كل جروب. إضافة فقط — باقي الدالة
          ومنطقها الأصلي (Part 12/15/25) متلمسش خالص.

نفس أسلوب الكود المتبع في courses/views.py و workshops/views.py:
function-based views + render + templates (مفيش class-based views).
"""

from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from workshops.models import LiveSession

from .access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from .forms import PaymentProofForm
from .live_provider import LiveProviderError, create_room, end_room, generate_access_token
from .models import (
    CurriculumCategory,
    GroupAssignment,
    GroupCapacityPlan,
    GroupChatMessage,
    GroupLiveSession,
    GroupMembership,
    GroupSubscription,
    GroupUpgrade,
    TeacherGroup,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_instructor(user) -> bool:
    """
    يتحقق من إن المستخدم مدرس، بالاعتماد على accounts.User.role اللي هو
    المرجع الرسمي لدور student/instructor في المشروع (زي ما اتوثق في
    Part 3 من PROGRESS.md).
    """
    return getattr(user, 'role', None) == 'instructor'


def instructor_required(view_func):
    """
    Decorator بيلف login_required + فحص إن request.user.role == 'instructor'.
    لو المستخدم مش مسجل دخول → بيوديه لصفحة اللوجين (سلوك login_required
    العادي). لو مسجل دخول بس مش مدرس → رسالة خطأ + ريدايركت للصفحة الرئيسية.
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _is_instructor(request.user):
            messages.error(request, 'الصفحة دي متاحة للمدرسين فقط.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped


def _is_student(user) -> bool:
    """
    يتحقق من إن المستخدم طالب، بنفس منطق _is_instructor بالظبط لكن بقيمة
    'student'. الافتراض إن قيمة role للطالب هي 'student' (مقابلة لـ
    'instructor' المستخدمة فعليًا فوق) — لو القيمة الحقيقية في
    accounts.User مختلفة، الفحص ده محتاج تعديل بسيط (سطر واحد).
    """
    return getattr(user, 'role', None) == 'student'


def student_required(view_func):
    """
    Decorator بيلف login_required + فحص إن request.user.role == 'student'.
    نفس فلسفة instructor_required بالظبط.
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _is_student(request.user):
            messages.error(request, 'الصفحة دي متاحة للطلاب فقط.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---------------------------------------------------------------------------
# Teacher Groups Dashboard
# ---------------------------------------------------------------------------

@instructor_required
def teacher_groups_dashboard(request):
    """
    يعرض كل TeacherGroup بتاعة المدرس الحالي، مع حالة الاشتراك، عدد الطلاب
    الحالي، والسعة القصوى.
    """
    groups = (
        TeacherGroup.objects
        .filter(teacher=request.user)
        .select_related('category', 'current_plan')
        .prefetch_related('subscriptions')
        .order_by('-created_at')
    )

    groups_data = []
    for group in groups:
        # آخر اشتراك (الأحدث) هو اللي بيمثل الحالة الفعلية للجروب دلوقتي.
        latest_subscription = group.subscriptions.order_by('-created_at').first()
        groups_data.append({
            'group': group,
            'subscription': latest_subscription,
            'current_students_count': group.current_students_count,
            'max_students': group.current_plan.max_students if group.current_plan else None,
            'seats_available': group.seats_available,
        })

    total_students = sum(row['current_students_count'] for row in groups_data)

    return render(request, 'groups/dashboard.html', {
        'groups_data': groups_data,
        'total_students': total_students,
    })


# ---------------------------------------------------------------------------
# Create Group
# ---------------------------------------------------------------------------

@instructor_required
def create_group(request):
    """
    GET: يعرض فورم اختيار فئة (country → stage → grade عن طريق AJAX cascading)
         واختيار باقة من GroupCapacityPlan مع عرض السعر.
    POST: يتحقق من عدم تكرار (teacher, category)، وينشئ TeacherGroup
          (is_active=False) و GroupSubscription (status='pending_payment').
    """
    active_plans = GroupCapacityPlan.objects.filter(is_active=True).order_by('max_students')

    if request.method == 'POST':
        category_id = request.POST.get('category')
        plan_id = request.POST.get('plan')

        if not category_id or not plan_id:
            messages.error(request, 'من فضلك اختار الفئة والباقة كاملين.')
            return render(request, 'groups/create_group.html', {
                'plans': active_plans,
            })

        category = get_object_or_404(CurriculumCategory, id=category_id, is_active=True)
        plan = get_object_or_404(GroupCapacityPlan, id=plan_id, is_active=True)

        if TeacherGroup.objects.filter(teacher=request.user, category=category).exists():
            messages.error(request, 'عندك بالفعل جروب لنفس الفئة دي.')
            return render(request, 'groups/create_group.html', {
                'plans': active_plans,
            })

        group = TeacherGroup.objects.create(
            teacher=request.user,
            category=category,
            current_plan=plan,
            is_active=False,
        )
        subscription = GroupSubscription.objects.create(
            group=group,
            plan=plan,
            status='pending_payment',
        )

        messages.success(
            request,
            'تم إنشاء الجروب بنجاح. الخطوة الجاية هي رفع إثبات الدفع عشان '
            'يتفعّل الجروب.',
        )
        # Part 8: بقى عندنا صفحة submit_payment_proof فعليًا، فبنودّي المدرس
        # لها مباشرة بدل ما نرجّعه للوحة التحكم (تفاصيل القرار ده كان موثق
        # في Part 7 كـ "حاجة محتاجة تعديل" — اتنفذ دلوقتي).
        return redirect('groups:submit_payment_proof', subscription_id=subscription.id)

    return render(request, 'groups/create_group.html', {
        'plans': active_plans,
    })


# ---------------------------------------------------------------------------
# AJAX: Cascading category dropdown (country -> stage -> grade)
# ---------------------------------------------------------------------------

@instructor_required
def category_options_json(request):
    """
    Endpoint بسيط لدعم الـ cascading dropdown في فورم إنشاء الجروب.

    - من غير أي بارامتر: بيرجع قايمة الدول المتاحة (country) بس.
    - مع ?country=X: بيرجع قايمة المراحل (stage) المتاحة لنفس الدولة.
    - مع ?country=X&stage=Y: بيرجع قايمة الصفوف (grade) المتاحة، وكل صف
      مرفق بيه الـ id بتاع CurriculumCategory المطابق (country+stage+grade)
      عشان الفرونت يقدر يحدد قيمة حقل category المخفي مباشرة من غير أي
      استعلام إضافي.
    """
    country = (request.GET.get('country') or '').strip()
    stage = (request.GET.get('stage') or '').strip()

    qs = CurriculumCategory.objects.filter(is_active=True)

    if not country:
        countries = (
            qs.order_by('country')
            .values_list('country', flat=True)
            .distinct()
        )
        return JsonResponse({'level': 'country', 'options': list(countries)})

    qs = qs.filter(country=country)

    if not stage:
        stages = (
            qs.order_by('stage')
            .values_list('stage', flat=True)
            .distinct()
        )
        return JsonResponse({'level': 'stage', 'options': list(stages)})

    qs = qs.filter(stage=stage)
    grades = [
        {'id': cat.id, 'grade': cat.grade}
        for cat in qs.order_by('grade')
    ]
    return JsonResponse({'level': 'grade', 'options': grades})


# ---------------------------------------------------------------------------
# Part 8: Submit Payment Proof
# ---------------------------------------------------------------------------

@instructor_required
def submit_payment_proof(request, subscription_id):
    """
    فورم لرفع إثبات دفع (receipt_image + transaction_reference) لاشتراك
    بحالة pending_payment بتاع المدرس الحالي بس.

    - ownership صارم: لو الاشتراك مش بتاع المدرس الحالي (عن طريق
      subscription.group.teacher)، PermissionDenied → 403.
    - لو فيه PaymentProof مرفوع بالفعل لنفس الاشتراك، بنمنع رفع تاني
      ونعرض رسالة إنه يستنى المراجعة (بدل ما نعرض الفورم تاني).
    - بعد الرفع بنجاح، الاشتراك بيفضل status='pending_payment' (زي ما هو
      أصلاً من وقت create_group في Part 7) — الفرق إن دلوقتي فيه PaymentProof
      مرتبط بيه في انتظار مراجعة الأدمن (Part 9).
    """
    subscription = get_object_or_404(
        GroupSubscription.objects.select_related('group', 'group__teacher', 'plan'),
        id=subscription_id,
    )

    # تحقق ownership صارم: الاشتراك لازم يكون تابع لجروب المدرس الحالي.
    if subscription.group.teacher_id != request.user.id:
        raise PermissionDenied('مش مسموحلك توصل للاشتراك ده.')

    existing_proof = subscription.proofs.order_by('-submitted_at').first()

    # لو فيه إثبات دفع مرفوع بالفعل، وهو لسه قيد المراجعة (الاشتراك لسه
    # pending_payment ومفيش review اتعمل عليه)، امنع رفع تاني.
    if existing_proof is not None and existing_proof.reviewed_at is None:
        messages.info(
            request,
            'إنت رفعت إثبات دفع لهذا الاشتراك بالفعل، وطلبك قيد المراجعة '
            'من الإدارة حاليًا. استنى الرد قبل رفع إثبات تاني.',
        )
        return render(request, 'groups/submit_payment_proof.html', {
            'subscription': subscription,
            'existing_proof': existing_proof,
            'form': None,
        })

    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.subscription = subscription
            proof.save()

            # الاشتراك يفضل pending_payment — ده أصلاً حالته من وقت
            # الإنشاء، وبيفضل كده لحد ما الأدمن يراجع (Part 9).
            subscription.status = 'pending_payment'
            subscription.save(update_fields=['status'])

            messages.success(
                request,
                'تم استلام طلبك وجاري المراجعة من الإدارة.',
            )
            return redirect('groups:teacher_dashboard')
    else:
        form = PaymentProofForm()

    return render(request, 'groups/submit_payment_proof.html', {
        'subscription': subscription,
        'existing_proof': None,
        'form': form,
    })


# ---------------------------------------------------------------------------
# Part 10: Upgrade Group Capacity
# ---------------------------------------------------------------------------

def _remaining_days(subscription):
    """
    عدد الأيام المتبقية (كسر عشري) لحد end_date بتاع اشتراك معين، بالنسبة
    لدلوقتي. بيرجع 0 لو مفيش end_date أو لو خلص أصلاً.
    """
    if not subscription or not subscription.end_date:
        return Decimal('0')
    delta = subscription.end_date - timezone.now()
    seconds_remaining = max(delta.total_seconds(), 0)
    return Decimal(seconds_remaining) / Decimal(86400)


def _calculate_upgrade_price(current_plan, new_plan, upgrade_mode, active_subscription):
    """
    يحسب فرق السعر حسب upgrade_mode المختار:

    - keep_end_date: (سعر الباقة الجديدة - سعر الباقة الحالية) * (الأيام
      المتبقية لحد end_date الحالي / 30)، مقرّب لأقرب رقمين عشريين.
      "الأيام المتبقية" بتتحسب من الاشتراك النشط الحالي بتاع الجروب. لو
      مفيش اشتراك نشط بتاريخ انتهاء واضح (حالة استثنائية مش متوقعة عمليًا
      لأن المدرس أصلاً محتاج اشتراك نشط عشان يوصل للصفحة دي)، بنعتبر الأيام
      المتبقية = 0 (يعني فرق = 0) بدل ما نفترض رقم عشوائي — القرار ده موثق
      هنا وفي PROGRESS.md.
    - reset_cycle: سعر الباقة الجديدة بالكامل (دورة شهرية جديدة من الصفر).

    الناتج مقرّب دايمًا لأقرب رقمين عشريين، ومتضمنش يكون أقل من صفر.
    """
    if upgrade_mode == 'reset_cycle':
        price_difference = new_plan.monthly_price
    else:  # keep_end_date
        remaining_days = _remaining_days(active_subscription)
        price_difference = (
            (new_plan.monthly_price - current_plan.monthly_price)
            * (remaining_days / Decimal('30'))
        )

    price_difference = price_difference.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if price_difference < 0:
        price_difference = Decimal('0.00')
    return price_difference


@instructor_required
def upgrade_group(request, group_id):
    """
    GET: يعرض للمدرس الباقات الأعلى من current_plan بتاعته بس، مع خيارين
         لطريقة الترقية (نفس تاريخ الانتهاء / تصفير الدورة).
    POST: يحسب فرق السعر حسب الاختيار، وينشئ GroupSubscription جديدة
          (status='pending_payment') + GroupUpgrade مربوطة بيها، ثم يودّي
          المدرس لصفحة رفع إثبات الدفع (Part 8) لدفع الفرق.
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('current_plan', 'category'),
        id=group_id,
    )

    # ownership صارم: الجروب لازم يكون بتاع المدرس الحالي.
    if group.teacher_id != request.user.id:
        raise PermissionDenied('مش مسموحلك توصل للجروب ده.')

    current_plan = group.current_plan
    if not current_plan:
        messages.error(
            request,
            'الجروب ده لسه معندوش باقة مفعّلة، لازم يكون عندك اشتراك نشط '
            'الأول قبل ما تعمل ترقية.',
        )
        return redirect('groups:teacher_dashboard')

    higher_plans = GroupCapacityPlan.objects.filter(
        is_active=True,
        max_students__gt=current_plan.max_students,
    ).order_by('max_students')

    active_subscription = (
        group.subscriptions
        .filter(status='active')
        .order_by('-end_date')
        .first()
    )

    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        upgrade_mode = request.POST.get('upgrade_mode')

        if not plan_id or upgrade_mode not in ('keep_end_date', 'reset_cycle'):
            messages.error(request, 'من فضلك اختار الباقة الجديدة وطريقة الترقية.')
            return render(request, 'groups/upgrade_group.html', {
                'group': group,
                'current_plan': current_plan,
                'higher_plans': higher_plans,
                'active_subscription': active_subscription,
            })

        new_plan = get_object_or_404(
            GroupCapacityPlan,
            id=plan_id,
            is_active=True,
            max_students__gt=current_plan.max_students,
        )

        price_difference = _calculate_upgrade_price(
            current_plan, new_plan, upgrade_mode, active_subscription,
        )

        new_subscription = GroupSubscription.objects.create(
            group=group,
            plan=new_plan,
            status='pending_payment',
            amount_paid=price_difference,
        )
        GroupUpgrade.objects.create(
            group=group,
            old_plan=current_plan,
            new_plan=new_plan,
            upgrade_mode=upgrade_mode,
            price_difference=price_difference,
            subscription=new_subscription,
        )

        messages.success(
            request,
            'تم إنشاء طلب الترقية بنجاح. الخطوة الجاية هي رفع إثبات دفع '
            'فرق السعر عشان يتفعّل.',
        )
        return redirect('groups:submit_payment_proof', subscription_id=new_subscription.id)

    return render(request, 'groups/upgrade_group.html', {
        'group': group,
        'current_plan': current_plan,
        'higher_plans': higher_plans,
        'active_subscription': active_subscription,
    })


# ---------------------------------------------------------------------------
# Part 11: Student joins a teacher's community
# ---------------------------------------------------------------------------

@student_required
def join_teacher_community(request, code):
    """
    GET: يعرض للطالب كل الفئات (CurriculumCategory) اللي المدرس صاحب الكود
         ده عنده فيها جروب is_active=True وseats_available > 0.

         الكود (join_code) بيتلاقى بيه TeacherGroup معين، لكن بمجرد ما نعرف
         مين المدرس بتاعه، بنعرض *كل* جروبات نفس المدرس المتاحة (مش الجروب
         بتاع الكود ده بس) — عشان "مجتمع المدرس" يبقى نقطة دخول واحدة تجمع
         كل الفئات اللي بيدرّسها، مش رابط منفصل لكل فئة على حدة. القرار ده
         موثق بالتفصيل في PROGRESS.md.

         الجروبات اللي وصلت للسعة القصوى (seats_available <= 0) بتتشال من
         القايمة تمامًا (مش بس تتعطل)، زي ما اتطلب بالظبط.

    POST: الطالب بيختار جروب واحد (group_id، بيمثل فئة واحدة) وينضم
          (GroupMembership جديد). العملية جوه transaction.atomic() +
          select_for_update() على الجروب المختار عشان نمنع أي race
          condition لو أكتر من طالب بيحاول ياخد آخر مكان متاح في نفس
          اللحظة. لو الجروب امتلأ بين ما الصفحة اتحملت وما الطالب دوس
          "انضمام" (حالة نادرة)، بيرجع رسالة "مفيش أماكن متاحة حاليًا في
          الفئة دي، تواصل مع المدرس" بدل ما يسمحله ينضم فوق السعة.

          الانضمام لفئات مختلفة عند نفس المدرس مسموح بالكامل. الانضمام
          مرتين لنفس الفئة (نفس group) ممنوع — GroupMembership.get_or_create
          بيتكفل بده من غير ما يرمي IntegrityError، بالاعتماد على
          unique_together('student', 'group') المعرّف في الموديل من Part 5.
    """
    entry_group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher'),
        join_code=code,
    )
    teacher = entry_group.teacher

    available_groups = (
        TeacherGroup.objects
        .filter(teacher=teacher, is_active=True)
        .select_related('category', 'current_plan')
        .order_by('category__country', 'category__stage', 'category__grade')
    )

    rows = []
    for group in available_groups:
        if group.seats_available <= 0:
            # مطلوب نخفيه تمامًا من القايمة، مش بس نعطّله.
            continue
        rows.append({
            'group': group,
            'category': group.category,
            'seats_available': group.seats_available,
            'already_joined': group.memberships.filter(student=request.user).exists(),
        })

    if request.method == 'POST':
        group_id = request.POST.get('group_id')

        with transaction.atomic():
            target_group = get_object_or_404(
                TeacherGroup.objects.select_for_update(),
                id=group_id,
                teacher=teacher,
                is_active=True,
            )

            if target_group.seats_available <= 0:
                messages.error(
                    request,
                    'مفيش أماكن متاحة حاليًا في الفئة دي، تواصل مع المدرس.',
                )
                return redirect('groups:join_teacher_community', code=code)

            _, created = GroupMembership.objects.get_or_create(
                student=request.user,
                group=target_group,
            )

        if created:
            messages.success(
                request,
                f'تم انضمامك لجروب "{target_group.category}" بنجاح.',
            )
        else:
            messages.info(request, 'إنت منضم بالفعل في الفئة دي.')

        return redirect('groups:join_teacher_community', code=code)

    return render(request, 'groups/join_teacher_community.html', {
        'teacher': teacher,
        'rows': rows,
        'code': code,
    })


# ---------------------------------------------------------------------------
# Part 12: Student "My Learning Groups" dashboard
# ---------------------------------------------------------------------------

def _get_active_subscription(group):
    """
    Part 15: helper بسيط لغرض العرض بس — بيرجع آخر GroupSubscription
    بحالة 'active' لنفس الجروب (لعرض end_date في التمبلتس، مثلاً).

    ده مختلف عن سؤال "هل محتوى الجروب متاح دلوقتي؟" (اللي هو سؤال
    صلاحيات، مش مجرد عرض) — السؤال ده بقى مسؤولية
    groups.access.is_group_content_accessible وحدها، عشان يبقى مصدر
    الحقيقة الوحيد المستخدم في كل الأماكن (هنا، وworkshops/views.py).
    قبل الجزء ده، الدالة المحلية _group_is_currently_active كانت بتعمل
    الاتنين (الفحص + جلب الاشتراك) مع بعض؛ اتقسّمت دلوقتي عشان الفحص
    الفعلي ميتكررش في أكتر من مكان.
    """
    return (
        group.subscriptions
        .filter(status='active')
        .order_by('-end_date')
        .first()
    )


@student_required
def my_learning_groups(request):
    """
    يعرض للطالب الحالي كل الجروبات المنضم فيها (عن طريق GroupMembership)،
    مع اسم المدرس والفئة وحالة الجروب (نشط / متجمد بسبب انتهاء اشتراك
    المدرس). كل جروب نشط بيتلف برابط واضح لمحتواه (Part 13/14 هيبنوا
    المحتوى الفعلي جوه نفس الصفحة اللي بيودّي ليها الرابط ده).
    """
    memberships = (
        GroupMembership.objects
        .filter(student=request.user)
        .select_related(
            'group', 'group__teacher', 'group__category', 'group__current_plan',
        )
        .order_by('-joined_at')
    )

    rows = []
    for membership in memberships:
        group = membership.group
        # Part 15: بدل _group_is_currently_active المحلية القديمة —
        # مصدر الحقيقة بقى groups.access.is_group_content_accessible.
        is_active = is_group_content_accessible(group)
        active_subscription = _get_active_subscription(group)
        # Part 25: لو الجروب نشط، بندوّر على أي GroupLiveSession شغالة
        # دلوقتي (status='live') عشان نعرض رابط "لايف دلوقتي" مباشر —
        # بنستعلم بس لو is_active (مفيش داعي للاستعلام على جروب متجمد،
        # لأن join_live_session هيرفضه بنفس الشرط أصلاً حتى لو كان فيه
        # لايف شغال بالمصادفة).
        live_session = (
            group.group_live_sessions.filter(status='live').first()
            if is_active else None
        )
        # Part 34 (المرحلة الثانية): عدد الواجبات المعلّقة (لسه ملهاش
        # تسليم من الطالب الحالي) في الجروب ده — نفس منطق live_session
        # فوق، بنستعلم بس لو الجروب نشط (مفيش داعي للاستعلام على جروب
        # متجمد، لأن submit_group_assignment هيرفض الطالب بنفس الشرط
        # أصلاً حتى لو كان فيه واجب معلّق بالمصادفة).
        pending_assignments_count = (
            group.assignments.exclude(submissions__student=request.user).count()
            if is_active else 0
        )
        rows.append({
            'membership': membership,
            'group': group,
            'teacher': group.teacher,
            'category': group.category,
            'is_active': is_active,
            'end_date': active_subscription.end_date if active_subscription else None,
            'live_session': live_session,
            'pending_assignments_count': pending_assignments_count,
        })

    return render(request, 'groups/my_learning_groups.html', {
        'rows': rows,
    })


# ---------------------------------------------------------------------------
# Part 24 (المرحلة الثانية): البث المباشر الجديد (GroupLiveSession / LiveKit)
# ---------------------------------------------------------------------------
#
# نظام منفصل تمامًا عن قسم "جلسات لايف" القديم فوق (workshops.LiveSession،
# Part 13، Google Meet). تفاصيل القرار المعماري الكامل في PROGRESS_PART22.md
# (Part 22/23). الـ views دي كلها بتتطلب إن المستخدم يكون المدرس صاحب
# الجروب بالظبط (نفس نمط ownership الصارم المستخدم في upgrade_group
# و submit_payment_proof — group.teacher_id != request.user.id -> 403).

def _get_owned_group_or_403(request, group_id):
    """
    Helper بسيط بيرجع TeacherGroup لو المستخدم الحالي هو المدرس صاحبه،
    وإلا PermissionDenied (403). نفس نمط الفحص المستخدم فعليًا في
    upgrade_group (Part 10) — مكرر هنا كـ helper عشان الثلاث views الجديدة
    (create_live_session، live_broadcast، end_live_session) ميكررش نفس
    الجملتين ثلاث مرات.
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )
    if group.teacher_id != request.user.id:
        raise PermissionDenied('مش مسموحلك توصل للجروب ده.')
    return group


@instructor_required
def create_live_session(request, group_id):
    """
    GET: يعرض فورم بسيط (title, description, mode, واختيار 'دلوقتي' أو
         'جدولة لوقت لاحق' مع حقل scheduled_at لو اختار الجدولة).
    POST:
      - لو 'دلوقتي': ينشئ GroupLiveSession (status='scheduled' مبدئيًا
        عشان يكون ليها pk قبل ما ننادي create_room)، ينادي create_room()
        من groups/live_provider.py، يحفظ room_identifier، يحوّل
        status='live' وstarted_at=now، وبيودّي المدرس مباشرة لصفحة البث
        (live_broadcast). لو create_room فشلت (LiveProviderError)، بنمسح
        السجل اللي اتعمل (مفيش داعي نسيب جلسة "scheduled" يتيمة بسبب فشل
        فني) ونرجّع رسالة خطأ واضحة.
      - لو 'جدولة': لازم scheduled_at، وبتتعمل GroupLiveSession
        status='scheduled' من غير أي نداء لـ LiveKit خالص (الروم بيتعمل
        لاحقًا لما المدرس فعليًا يدخل يبدأ البث — مفيش view لسه بيعمل ده
        من صفحة الجلسات المجدولة؛ ⚠️ ملحوظة مفتوحة تحت في PROGRESS).
    """
    group = _get_owned_group_or_403(request, group_id)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        mode = request.POST.get('mode')
        start_choice = request.POST.get('start_choice')  # 'now' | 'schedule'

        valid_modes = {choice for choice, _ in GroupLiveSession.MODE_CHOICES}
        if not title or mode not in valid_modes or start_choice not in ('now', 'schedule'):
            messages.error(request, 'من فضلك املأ العنوان ونوع البث بشكل صحيح.')
            return render(request, 'groups/create_live_session.html', {
                'group': group,
                'mode_choices': GroupLiveSession.MODE_CHOICES,
            })

        if start_choice == 'schedule':
            scheduled_at_raw = request.POST.get('scheduled_at')
            if not scheduled_at_raw:
                messages.error(request, 'من فضلك حدد ميعاد اللايف المجدول.')
                return render(request, 'groups/create_live_session.html', {
                    'group': group,
                    'mode_choices': GroupLiveSession.MODE_CHOICES,
                })
            parsed_scheduled_at = timezone.datetime.fromisoformat(scheduled_at_raw)
            if timezone.is_naive(parsed_scheduled_at):
                parsed_scheduled_at = timezone.make_aware(parsed_scheduled_at)

            GroupLiveSession.objects.create(
                group=group,
                host=request.user,
                title=title,
                description=description,
                mode=mode,
                status='scheduled',
                scheduled_at=parsed_scheduled_at,
            )
            messages.success(request, 'تم جدولة اللايف بنجاح. هيظهر في قايمة الجلسات القادمة.')
            return redirect('groups:group_detail', group_id=group.id)

        # start_choice == 'now'
        session = GroupLiveSession.objects.create(
            group=group,
            host=request.user,
            title=title,
            description=description,
            mode=mode,
            status='scheduled',
        )
        try:
            room_name = create_room(session)
        except LiveProviderError as exc:
            session.delete()
            messages.error(request, f'تعذر بدء البث دلوقتي: {exc}')
            return redirect('groups:group_detail', group_id=group.id)

        session.room_identifier = room_name
        session.status = 'live'
        session.started_at = timezone.now()
        session.save(update_fields=['room_identifier', 'status', 'started_at'])

        return redirect('groups:live_broadcast', group_id=group.id, session_id=session.id)

    return render(request, 'groups/create_live_session.html', {
        'group': group,
        'mode_choices': GroupLiveSession.MODE_CHOICES,
    })


@instructor_required
def live_broadcast(request, group_id, session_id):
    """
    صفحة البث نفسها للمدرس (المضيف) — فيها عميل الـ WebRTC (LiveKit JS
    Client SDK) اللي بيتصل بالروم عن طريق access token (role='host')
    وبينشر الكاميرا و/أو مشاركة الشاشة حسب mode الجلسة.

    لازم الجلسة تكون status='live' وبتاعة نفس المدرس (host) — لو مش كده
    (مثلاً اتقفلت من تاب تاني، أو لسه scheduled)، بنرجّعه لصفحة الجروب
    برسالة واضحة بدل ما نعرض صفحة بث لجلسة مش شغالة.
    """
    group = _get_owned_group_or_403(request, group_id)
    session = get_object_or_404(GroupLiveSession, id=session_id, group=group)

    if session.host_id != request.user.id:
        raise PermissionDenied('إنت مش مضيف الجلسة دي.')

    if session.status != 'live':
        messages.error(request, 'الجلسة دي مش شغالة دلوقتي (لسه متجدولة أو خلصت بالفعل).')
        return redirect('groups:group_detail', group_id=group.id)

    try:
        token = generate_access_token(session, request.user, role='host')
    except LiveProviderError as exc:
        messages.error(request, f'تعذر الاتصال بخدمة البث: {exc}')
        return redirect('groups:group_detail', group_id=group.id)

    return render(request, 'groups/live_broadcast.html', {
        'group': group,
        'session': session,
        'livekit_url': settings.LIVEKIT_URL,
        'livekit_token': token,
    })


@instructor_required
@require_POST
def end_live_session(request, group_id, session_id):
    """
    زرار "إنهاء البث" — بينادي end_room() من live_provider.py (بيقفل
    الروم فعليًا عند LiveKit)، وبيحدّث status='ended' + ended_at.
    POST بس (نفس نمط attach/detach_session في group_detail).
    """
    group = _get_owned_group_or_403(request, group_id)
    session = get_object_or_404(GroupLiveSession, id=session_id, group=group)

    if session.host_id != request.user.id:
        raise PermissionDenied('إنت مش مضيف الجلسة دي.')

    if session.status == 'live':
        try:
            end_room(session)
        except LiveProviderError as exc:
            # end_room نفسها بتتعامل مع "الروم مش موجود" بهدوء (log warning
            # بس)، فأي LiveProviderError هنا يبقى فشل حقيقي في الإعدادات
            # (مفتاح API غلط مثلاً) — نعرضه للمدرس لكن برضه نقفل الجلسة
            # محليًا عشان مايفضلش عالق في status='live' غلط.
            messages.warning(
                request,
                f'اتقفلت الجلسة محليًا، لكن حصل خطأ في التواصل مع خدمة البث: {exc}',
            )
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save(update_fields=['status', 'ended_at'])
        messages.success(request, 'تم إنهاء البث بنجاح.')
    else:
        messages.info(request, 'الجلسة دي مش شغالة أصلاً.')

    return redirect('groups:group_detail', group_id=group.id)


# ---------------------------------------------------------------------------
# Part 25 (المرحلة الثانية): واجهة الطالب — الانضمام للايف داخل الجروب
# ---------------------------------------------------------------------------
#
# مكمل مباشر لـ Part 24 (البث المباشر الجديد GroupLiveSession/LiveKit).
# الفرق الجوهري عن create_live_session/live_broadcast (Part 24، للمدرس/
# host): هنا المستخدم لازم يكون طالب عضو (GroupMembership) مش صاحب
# الجروب، وrole='viewer' في generate_access_token (مفيش أي صلاحية نشر
# كاميرا/شاشة — can_publish=False متضمنة في الدالة دي من Part 23).

@student_required
def join_live_session(request, session_id):
    """
    نقطة الدخول الوحيدة للطالب لأي GroupLiveSession — السلوك بيختلف حسب
    session.status:

      - 'scheduled': لسه مبدأش، بنعرض شاشة انتظار بسيطة فيها الميعاد
        المتوقع، من غير أي نداء لـ LiveKit خالص (الروم أصلاً لسه مالوش
        وجود عند المزود — create_room() بتتنادى بس وقت ما المدرس فعليًا
        يبدأ البث من create_live_session، Part 24). الصفحة فيها
        meta-refresh بسيط كل 30 ثانية عشان الطالب يلاقي نفسه اتنقل
        لصفحة المشاهدة تلقائيًا لو المدرس بدأ اللايف، من غير ما يحتاج
        يعمل ريفريش يدوي — ده تحسين UX بسيط بـ HTML/meta بس، مفيش أي
        JS polling حقيقي أو WebSocket (نفس فلسفة باقي المشروع: مفيش
        real-time غير لو Django Channels موجودة أصلاً — مش الحالة هنا).
      - 'live': بننادي generate_access_token(role='viewer') ونعرض صفحة
        المشاهدة (عميل LiveKit JS بيعمل subscribe بس لأي track المدرس
        بينشره، من غير أي صلاحية نشر).
      - 'ended': ⚠️ حسب خريطة الأجزاء، المفروض نوجّه الطالب تلقائيًا
        لصفحة التسجيل — لكن صفحة/نظام التسجيل (Part 26) لسه معملوش، فبدل
        ما نعمل redirect لصفحة/URL مش موجود (هيكسر)، بنرجّعه لصفحة
        الجروب برسالة واضحة توضح إن التسجيل هيتاح قريبًا. ⚠️ ملحوظة
        مفتوحة موثقة بالتفصيل في PROGRESS (Part 25) — لازم تتصلح تلقائيًا
        لما Part 26 يتنفذ (نبدّل الـ redirect بـ redirect حقيقي لصفحة
        التسجيل الجديدة).
      - 'canceled' (أو أي قيمة غير متوقعة): رسالة بسيطة + رجوع لصفحة
        الجروب.

    الصلاحية: تحقق صارم إن الطالب عضو فعلي (GroupMembership) في الجروب
    بتاع الجلسة دي، وإن is_group_content_accessible(group) بترجع True
    (يعني اشتراك المدرس نشط دلوقتي) — بنفس الدالة المستخدمة في كل مكان
    تاني في المشروع من Part 15 (watch_live/watch_recording في
    workshops/views.py، group_detail هنا)، من غير أي منطق بديل. لو مش
    عضو → PermissionDenied (403). لو عضو لكن الجروب متجمد →
    GROUP_FROZEN_MESSAGE + ريدايركت لـ my_learning_groups (بنفس رسالة
    ونمط group_detail بالظبط).
    """
    session = get_object_or_404(
        GroupLiveSession.objects.select_related('group', 'group__teacher', 'group__category'),
        id=session_id,
    )
    group = session.group

    is_member = GroupMembership.objects.filter(
        student=request.user, group=group,
    ).exists()
    if not is_member:
        raise PermissionDenied('إنت مش عضو في الجروب ده.')

    if not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    if session.status == 'scheduled':
        return render(request, 'groups/watch_live_session.html', {
            'group': group,
            'session': session,
            'view_mode': 'waiting',
        })

    if session.status == 'live':
        try:
            token = generate_access_token(session, request.user, role='viewer')
        except LiveProviderError as exc:
            messages.error(request, f'تعذر الاتصال بخدمة البث: {exc}')
            return redirect('groups:group_detail', group_id=group.id)

        return render(request, 'groups/watch_live_session.html', {
            'group': group,
            'session': session,
            'view_mode': 'live',
            'livekit_url': settings.LIVEKIT_URL,
            'livekit_token': token,
        })

    if session.status == 'ended':
        # ✅ [تحديث Part 26 — نسخة معدّلة]: التسجيل بقى بيترفع يدويًا من
        # المدرس (مش تلقائي عن طريق أي إيجرس/webhook). لو recording_file
        # اتملى بالفعل (المدرس رفع الملف)، نوجّه الطالب لصفحة المشاهدة
        # مباشرة زي ما اتطلب أصلاً في خريطة الأجزاء. لو لسه فاضي (المدرس
        # لسه ما رفعش)، بنعرض رسالة واضحة توضح إن التسجيل لسه مش متاح.
        if session.recording_file:
            return redirect('groups:watch_group_recording', session_id=session.id)
        messages.info(
            request,
            'البث ده خلص، والمدرس لسه ما رفعش التسجيل — جرب تاني بعد شوية.',
        )
        return redirect('groups:group_detail', group_id=group.id)

    # status == 'canceled' (أو أي قيمة غير متوقعة مستقبلًا).
    messages.info(request, 'البث ده اتلغى أو مش متاح دلوقتي.')
    return redirect('groups:group_detail', group_id=group.id)


# ---------------------------------------------------------------------------
# Part 26 (نسخة معدّلة — Manual Recording Upload): رفع التسجيل يدويًا +
# مكتبة الفيديوهات المسجلة (VOD)
# ---------------------------------------------------------------------------
#
# التسجيل بقى مسؤولية المدرس بالكامل: يسجل الشاشة/الاجتماع بأي طريقة
# يفضّلها (OBS / Zoom Recording / إلخ) خارج المنصة، وبعد ما اللايف يخلص
# (session.status == 'ended') يرفع الملف يدويًا من upload_group_recording
# تحت. مفيش أي تفعيل تلقائي للتسجيل عند LiveKit، ومفيش أي webhook بيحدّث
# أي حاجة تلقائيًا (groups/webhooks.py رجع endpoint فاضي — تفاصيل هناك).
# نفس فحص الصلاحية بالظبط المستخدم في group_detail وjoin_live_session
# (Part 15/25): GroupMembership + is_group_content_accessible للطالب،
# ودخول دايمًا للمدرس صاحب الجروب.

# الصيغ المسموحة لملف التسجيل — زي ما اتطلب بالظبط في نص الجزء (mp4،
# webm، mov). التحقق بيتم من امتداد اسم الملف بس (نفس مستوى التحقق
# البسيط المستخدم في باقي المشروع، زي فحص نوع الصورة في PaymentProofForm
# — مفيش أي مكتبة فحص محتوى الملف الفعلي زي python-magic في المشروع).
_ALLOWED_RECORDING_EXTENSIONS = {'mp4', 'webm', 'mov'}

# ---------------------------------------------------------------------------
# Part 30 (المرحلة الثانية): إرفاق صور/ملفات في الشات الجماعي.
#
# نفس مستوى التحقق البسيط المستخدم في _ALLOWED_RECORDING_EXTENSIONS فوق
# (فحص امتداد اسم الملف بس، مفيش مكتبة فحص محتوى فعلي زي python-magic في
# المشروع) — بس هنا كـ ثابتين منفصلين (صور/ملفات) مش من settings.py، لإن
# نص طلب الجزء ده مقالش صراحة "ضيف إعداد في settings" (بعكس Part 26 اللي
# طلب صراحة "حسب إعدادات المشروع")، فاخترت الاتساق مع
# _ALLOWED_RECORDING_EXTENSIONS (ثابت في الملف نفسه) بدل ما أضيف إعداد
# جديد في settings.py من غير طلب صريح. سهل تحويلهم لـ settings.config()
# لاحقًا لو Ahmed عايز يتحكم فيهم من غير ما يلمس الكود.
_ALLOWED_CHAT_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
_ALLOWED_CHAT_FILE_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar',
}
_CHAT_IMAGE_MAX_BYTES = 5 * 1024 * 1024   # 5 ميجا — اخترتها بنفسي، مفيش تحديد صريح في الطلب.
_CHAT_FILE_MAX_BYTES = 15 * 1024 * 1024   # 15 ميجا — نفس الملحوظة.


def _get_group_and_membership_or_403(request, group):
    """
    Helper بسيط بيرجع (is_owner, is_member) لجروب معين، ويرمي
    PermissionDenied لو المستخدم مش عضو ولا صاحب — نفس الفحص المكرر
    بالحرف في group_detail (Part 13/15) وjoin_live_session (Part 25)،
    اتلم هنا في helper واحد عشان الـ views الجديدة (group_recordings،
    watch_group_recording) ميكرروش نفس السطرين مرتين.
    """
    is_owner = group.teacher_id == request.user.id
    is_member = GroupMembership.objects.filter(
        student=request.user, group=group,
    ).exists()
    if not (is_owner or is_member):
        raise PermissionDenied('إنت مش عضو ولا صاحب الجروب ده.')
    return is_owner, is_member


@login_required
def group_recordings(request, group_id):
    """
    مكتبة فيديوهات — كل GroupLiveSession بحالة status='ended' وليها
    recording_file فعلي (يعني المدرس رفع التسجيل يدويًا بالفعل)، لأعضاء
    الجروب بس (أو المدرس صاحبه).

    Part 26 (نسخة معدّلة): الفلترة بقت على recording_file (رفع يدوي) بدل
    recording_url (كان بيتملى تلقائيًا من الإيجرس، النظام القديم الملغي).

    نفس فحص الصلاحية المستخدم في group_detail/join_live_session بالظبط:
    عضوية فعلية (أو ownership)، وبعدين — للطالب العضو بس (مش المدرس) —
    لازم الجروب يكون "نشط" (is_group_content_accessible) وإلا بيترجع
    لصفحة "جروباتي" برسالة التجميد المعتادة. المدرس صاحب الجروب يقدر
    يشوف مكتبة التسجيلات حتى لو الجروب متجمد (نفس استثناء group_detail).
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    recordings = (
        group.group_live_sessions
        .filter(status='ended')
        .exclude(recording_file='')
        .order_by('-ended_at')
    )

    return render(request, 'groups/group_recordings.html', {
        'group': group,
        'is_owner': is_owner,
        'recordings': recordings,
    })


@login_required
def watch_group_recording(request, session_id):
    """
    صفحة مشاهدة تسجيل واحد (مشغل فيديو HTML5 بسيط لـ recording_file).

    Part 26 (نسخة معدّلة): الشرط بقى على recording_file بدل recording_url.

    نفس فحص الصلاحية بالظبط زي group_recordings/join_live_session —
    الجلسة بتتحدد بـ session_id مباشرة (مش محتاجين group_id في الـ URL،
    نفس فلسفة join_live_session في Part 25) والجروب بيتستنتج منها.
    """
    session = get_object_or_404(
        GroupLiveSession.objects.select_related('group', 'group__teacher', 'group__category'),
        id=session_id,
    )
    group = session.group
    is_owner, is_member = _get_group_and_membership_or_403(request, group)

    if is_member and not is_owner and not is_group_content_accessible(group):
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    if session.status != 'ended' or not session.recording_file:
        messages.info(request, 'التسجيل ده مش متاح دلوقتي.')
        return redirect('groups:group_recordings', group_id=group.id)

    return render(request, 'groups/watch_group_recording.html', {
        'group': group,
        'session': session,
        'is_owner': is_owner,
    })


@instructor_required
def upload_group_recording(request, session_id):
    """
    Part 26 (نسخة معدّلة — Manual Recording Upload):

    رفع تسجيل اللايف يدويًا بعد ما الجلسة تخلص. مسموح بس لـ:
      - مدرس الجروب (host الجلسة)، أو
      - Owner (صاحب الجروب — نفس نمط ownership المستخدم في create_live_session
        وend_live_session، group.teacher_id).
    في المشروع ده الاتنين نفس الشخص فعليًا دايمًا (المدرس هو صاحب الجروب
    وهو نفسه host أي جلسة بيعملها — مفيش مفهوم "مدرس مساعد" في المشروع
    لحد دلوقتي)، فالفحص بيتم على group.teacher_id زي باقي views البث
    المباشر كلها (create_live_session/live_broadcast/end_live_session)
    من غير أي فحص إضافي على session.host_id تحديدًا.

    الشروط:
      - session.status == 'ended' — يمنع رفع تسجيل قبل ما اللايف ينتهي
        فعليًا (نفس المتطلب المطلوب بالظبط).
      - صيغة الملف من ضمن mp4/webm/mov (فحص الامتداد بس).
      - حجم الملف <= GROUP_LIVE_RECORDING_MAX_UPLOAD_MB (settings.py).

    بعد النجاح: بيحفظ الملف بنفس Storage Backend المستخدم لملفات
    الكورسات (FileField عادي فوق DEFAULT_FILE_STORAGE — نفس أسلوب
    courses.models.VideoFile.file بالظبط، من غير أي تخزين خارجي جديد)،
    ويحدّث recording_uploaded_at، ويعرض رسالة نجاح.
    """
    session = get_object_or_404(
        GroupLiveSession.objects.select_related('group', 'group__teacher', 'group__category'),
        id=session_id,
    )
    group = session.group
    if group.teacher_id != request.user.id:
        raise PermissionDenied('مش مسموحلك ترفع تسجيل لهذا اللايف.')

    if session.status != 'ended':
        messages.error(request, 'التسجيل بيترفع بس بعد ما اللايف ينتهي فعليًا.')
        return redirect('groups:group_detail', group_id=group.id)

    if request.method == 'POST':
        uploaded_file = request.FILES.get('recording_file')

        if not uploaded_file:
            messages.error(request, 'من فضلك اختار ملف الفيديو الأول.')
            return render(request, 'groups/upload_group_recording.html', {
                'group': group,
                'session': session,
            })

        ext = os.path.splitext(uploaded_file.name)[1].lstrip('.').lower()
        if ext not in _ALLOWED_RECORDING_EXTENSIONS:
            messages.error(
                request,
                'صيغة الملف غير مدعومة — الصيغ المسموحة: mp4, webm, mov.',
            )
            return render(request, 'groups/upload_group_recording.html', {
                'group': group,
                'session': session,
            })

        max_bytes = settings.GROUP_LIVE_RECORDING_MAX_UPLOAD_MB * 1024 * 1024
        if uploaded_file.size > max_bytes:
            messages.error(
                request,
                f'حجم الملف أكبر من الحد المسموح '
                f'({settings.GROUP_LIVE_RECORDING_MAX_UPLOAD_MB} ميجا).',
            )
            return render(request, 'groups/upload_group_recording.html', {
                'group': group,
                'session': session,
            })

        session.recording_file = uploaded_file
        session.recording_uploaded_at = timezone.now()
        session.save(update_fields=['recording_file', 'recording_uploaded_at'])

        messages.success(request, 'تم رفع التسجيل بنجاح — هيظهر دلوقتي في مكتبة التسجيلات.')
        return redirect('groups:group_detail', group_id=group.id)

    return render(request, 'groups/upload_group_recording.html', {
        'group': group,
        'session': session,
    })


# ---------------------------------------------------------------------------
# Part 29 (المرحلة الثانية): وضع "الإذاعة" في الشات الجماعي
# ---------------------------------------------------------------------------
#
# زرار/سويتش بسيط في صفحة الجروب، ظاهر للمدرس صاحب الجروب بس، بيبدّل
# TeacherGroup.chat_mode بين 'open' (الوضع الافتراضي — أي عضو يقدر يكتب)
# و'broadcast_only' (المدرس بس يقدر يبعت رسائل). اتعمل كـ view مستقلة
# (مش action تاني جوه group_detail زي send_message/attach_session) عشان
# يبقى مسار URL واضح ومباشر (POST بس) بنفس نمط end_live_session —
# مفيش أي منطق تاني غير التبديل والريدايركت.

@instructor_required
@require_POST
def toggle_chat_mode(request, group_id):
    """
    يبدّل group.chat_mode بين 'open' و'broadcast_only'. مقصور على المدرس
    صاحب الجروب بس (_get_owned_group_or_403 → 403 لو مش صاحبه). بعد
    التبديل بيرجّع المستخدم لصفحة الجروب برسالة توضح الحالة الجديدة.
    """
    group = _get_owned_group_or_403(request, group_id)

    group.chat_mode = 'open' if group.chat_mode == 'broadcast_only' else 'broadcast_only'
    group.save(update_fields=['chat_mode'])

    if group.chat_mode == 'broadcast_only':
        messages.success(
            request,
            'تم قفل الشات على وضع الإذاعة — إنت بس اللي هتقدر تبعت رسائل دلوقتي.',
        )
    else:
        messages.success(
            request,
            'تم فتح الشات تاني — كل الأعضاء يقدروا يبعتوا رسائل.',
        )

    return redirect('groups:group_detail', group_id=group.id)


# ---------------------------------------------------------------------------
# Part 12/13: Group content page
# ---------------------------------------------------------------------------

@instructor_required
def group_members(request, group_id):
    """
    Part 37 (المرحلة الثانية) — مركز تنقل موحّد داخل الجروب.

    تاب "الأعضاء" في شريط التابات الجديد (_group_tabs.html) — مش كان
    موجود أي view/صفحة زي دي قبل كده في المرحلة التانية (راجعت urls.py
    و views.py القديمة قبل الإضافة، مفيش أي مسار بيعرض قايمة أعضاء
    الجروب). زي ما اتطلب صراحة في نص Part 37 ("الأعضاء تظهر للمدرس بس")،
    الـ view دي:
      - محمية بـ instructor_required + _get_owned_group_or_403 (نفس نمط
        create_live_session/live_broadcast من Part 24 بالحرف) — لو حد
        مش المدرس صاحب الجروب حاول يوصلها، PermissionDenied (403).
      - بترجع كل GroupMembership بتاعة الجروب ده (نفس الموديل من Part 5)
        مرتبة بالأحدث انضمامًا أول، مع select_related('student') لتقليل
        عدد الاستعلامات.
    مفيش أي migration أو تعديل على أي موديل هنا — GroupMembership كانت
    جاهزة بالكامل من Part 5.
    """
    group = _get_owned_group_or_403(request, group_id)
    members = (
        GroupMembership.objects
        .filter(group=group)
        .select_related('student')
        .order_by('-joined_at')
    )
    context = {
        'group': group,
        'is_owner': True,
        'members': members,
    }
    return render(request, 'groups/group_members.html', context)


@login_required
def group_detail(request, group_id):
    """
    صفحة محتوى الجروب.

    Part 12: كانت placeholder بسيط (اسم المدرس، الفئة، حالة الاشتراك)
    ومحمية بـ @student_required بس (يعني المدرس صاحب الجروب نفسه ماكانش
    يقدر يفتحها أصلاً).

    Part 13: اتوسّعت لعرض جلسات اللايف (LiveSession) التابعة للجروب ده،
    وده كشف ثغرة صلاحيات من Part 12 لازم تتصلح دلوقتي: متطلبات الجزء ده
    صراحة بتقول "بس GroupMembership بتوع الجروب ده + المدرس صاحب الجروب"
    — يعني المدرس لازم يقدر يشوف صفحة جروبه. عشان كده استبدلت
    @student_required بـ @login_required + فحص يدوي بيسمح لصاحبين:
      1) المدرس صاحب الجروب (group.teacher) — دخول دايمًا، حتى لو الجروب
         متجمد (عشان يقدر يشوف حالته ويجدد الاشتراك من هنا).
      2) الطالب العضو (GroupMembership) — دخول بس لو الجروب "نشط"
         (زي منطق Part 12 الأصلي بالظبط)؛ لو متجمد بيترد لصفحة
         "جروباتي" برسالة واضحة زي ما كان.

    غير كده (مش عضو ولا صاحب الجروب) → PermissionDenied (403).

    الجلسات المعروضة: بتتقسم لـ "شغالة دلوقتي" (active) و"جاية" (upcoming)
    لكل الزوار، وقايمة إدارة كاملة (كل جلسات الجروب + جلسات المدرس اللي
    لسه مش مربوطة بأي جروب عشان يقدر يربطها) للمدرس صاحب الجروب بس.

    Part 14: اتوسّعت تاني عشان تعرض شات الجروب الجماعي (GroupChatMessage)
    وتستقبل رسائل جديدة. بدل ما نعمل view/URL منفصل (زي
    'groups:group_chat')، استخدمنا نفس نمط الـ POST action dispatch اللي
    Part 13 عملته بالظبط لـ attach_session/detach_session، وضفنا
    action='send_message' ليه:
      - الفرق الوحيد: attach/detach_session مقصورين على is_owner، لكن
        send_message متاح لأي حد وصل للصفحة دي أصلاً (يعني إما is_owner
        أو is_member) — لإن الفحص فوق (is_member and not is_owner and not
        is_active) بيرد أي طالب في جروب متجمد لصفحة "جروباتي" *قبل* ما
        نوصل لمنطق الـ POST خالص، فأي حد لسه واصل هنا يبقى مسموحله
        يبعت رسالة أصلاً (مالك، أو طالب في جروب نشط).
      - القرار ده موثق بالتفصيل في PROGRESS.md (Part 14) مع سبب اختيار
        GroupChatMessage في groups/models.py بدل ربطها بـ mentorship.

    Part 24 (المرحلة الثانية): اتضاف قسم "اللايف المباشر" جديد (منفصل
    تمامًا عن قسم "جلسات لايف" القديم فوق) بيعرض GroupLiveSession النشطة
    حاليًا (status='live') والمجدولة القادمة (status='scheduled')، مع
    زرار "ابدأ بث مباشر" للمدرس لو مفيش لايف شغال دلوقتي.

    Part 29 (المرحلة الثانية): action='send_message' بقى بيتحقق كمان من
    group.chat_mode — لو 'broadcast_only' وممش is_owner، بيترفض الإرسال
    برسالة واضحة (تفاصيل كاملة جوه الشرط نفسه تحت). التمبلت بيخفي حقل
    الكتابة نهائيًا للطلاب في الوضع ده، والفحص هنا هو خط الدفاع الحقيقي
    (server-side) ضد أي POST مباشر متجاوز للواجهة.
    """
    group = get_object_or_404(
        TeacherGroup.objects.select_related('teacher', 'category'),
        id=group_id,
    )

    is_owner = group.teacher_id == request.user.id
    is_member = GroupMembership.objects.filter(
        student=request.user, group=group,
    ).exists()

    if not (is_owner or is_member):
        raise PermissionDenied('إنت مش عضو ولا صاحب الجروب ده.')

    # Part 15: بدل _group_is_currently_active المحلية القديمة —
    # مصدر الحقيقة بقى groups.access.is_group_content_accessible.
    is_active = is_group_content_accessible(group)
    active_subscription = _get_active_subscription(group)

    if is_member and not is_owner and not is_active:
        messages.error(request, GROUP_FROZEN_MESSAGE)
        return redirect('groups:my_learning_groups')

    # Part 13/14: كل أكشنز الـ POST في صفحة الجروب بتتبعت لنفس الـ URL دي
    # بحقل مخفي "action" بيحدد المطلوب.
    # - attach_session / detach_session: المدرس صاحب الجروب بس (Part 13).
    # - send_message: أي حد وصل للسطر ده أصلاً (مالك أو طالب في جروب نشط —
    #   الفحص فوق رجّع أي طالب في جروب متجمد قبل كده)، Part 14.
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'attach_session' and is_owner:
            session_id = request.POST.get('session_id')
            session_to_attach = get_object_or_404(
                LiveSession,
                id=session_id,
                instructor=request.user,
                group__isnull=True,
            )
            session_to_attach.group = group
            session_to_attach.save(update_fields=['group'])
            messages.success(request, 'تم ربط الجلسة بالجروب بنجاح.')
            return redirect('groups:group_detail', group_id=group.id)

        if action == 'detach_session' and is_owner:
            session_id = request.POST.get('session_id')
            session_to_detach = get_object_or_404(
                LiveSession, id=session_id, instructor=request.user, group=group,
            )
            session_to_detach.group = None
            session_to_detach.save(update_fields=['group'])
            messages.info(request, 'تم فك ربط الجلسة من الجروب.')
            return redirect('groups:group_detail', group_id=group.id)

        if action == 'send_message':
            # Part 29: لو الجروب في وضع "إذاعة" (broadcast_only)، مفيش حد
            # يقدر يبعت رسالة (نص، صورة، أو ملف) غير المدرس صاحب الجروب.
            # الفحص هنا هو خط الدفاع الحقيقي (server-side) — التمبلت بيخفي
            # فورم الإرسال بالكامل (نص + رفع) أصلاً للطلاب في الوضع ده،
            # لكن لو حد بعت POST مباشر (متجاوز الواجهة)، لازم يترفض هنا
            # برضه. الفحص ده قبل أي قراءة لمحتوى/ملفات الطلب عمدًا.
            if group.chat_mode == 'broadcast_only' and not is_owner:
                messages.error(
                    request,
                    'المدرس قافل الشات دلوقتي، بس هو اللي يقدر يبعت رسائل.',
                )
                return redirect('groups:group_detail', group_id=group.id)

            content = (request.POST.get('content') or '').strip()
            image_file = request.FILES.get('attachment_image')
            file_file = request.FILES.get('attachment_file')

            # Part 30: رسالة واحدة بيبقى ليها نوع واحد بس — نص، أو صورة،
            # أو ملف. مش مسموح تبعت صورة وملف في نفس الرسالة (تبسيط
            # مقصود، مفيش تحديد صريح في الطلب لدعم أكتر من مرفق في نفس
            # الوقت). لو الاتنين اتبعتوا مع بعض بالغلط، بنرفض برسالة
            # واضحة بدل ما نختار واحد عشوائيًا.
            if image_file and file_file:
                messages.error(
                    request,
                    'ابعت صورة أو ملف في الرسالة، مش الاثنين مع بعض.',
                )
                return redirect('groups:group_detail', group_id=group.id)

            if image_file:
                ext = os.path.splitext(image_file.name)[1].lstrip('.').lower()
                if ext not in _ALLOWED_CHAT_IMAGE_EXTENSIONS:
                    messages.error(
                        request,
                        'صيغة الصورة غير مدعومة — الصيغ المسموحة: '
                        'jpg, jpeg, png, gif, webp.',
                    )
                    return redirect('groups:group_detail', group_id=group.id)
                if image_file.size > _CHAT_IMAGE_MAX_BYTES:
                    messages.error(
                        request,
                        'حجم الصورة أكبر من الحد المسموح (5 ميجا).',
                    )
                    return redirect('groups:group_detail', group_id=group.id)
                GroupChatMessage.objects.create(
                    group=group,
                    sender=request.user,
                    content=content,
                    message_type='image',
                    attachment_image=image_file,
                )
                return redirect('groups:group_detail', group_id=group.id)

            if file_file:
                ext = os.path.splitext(file_file.name)[1].lstrip('.').lower()
                if ext not in _ALLOWED_CHAT_FILE_EXTENSIONS:
                    messages.error(
                        request,
                        'نوع الملف غير مدعوم — الأنواع المسموحة: '
                        'pdf, doc, docx, xls, xlsx, ppt, pptx, txt, zip, rar.',
                    )
                    return redirect('groups:group_detail', group_id=group.id)
                if file_file.size > _CHAT_FILE_MAX_BYTES:
                    messages.error(
                        request,
                        'حجم الملف أكبر من الحد المسموح (15 ميجا).',
                    )
                    return redirect('groups:group_detail', group_id=group.id)
                GroupChatMessage.objects.create(
                    group=group,
                    sender=request.user,
                    content=content,
                    message_type='file',
                    attachment_file=file_file,
                )
                return redirect('groups:group_detail', group_id=group.id)

            # مفيش أي مرفق — رسالة نصية عادية (نفس سلوك Part 14 بالحرف).
            if content:
                GroupChatMessage.objects.create(
                    group=group,
                    sender=request.user,
                    content=content,
                    message_type='text',
                )
            else:
                messages.error(request, 'اكتب رسالة أو ارفق صورة/ملف قبل الإرسال.')
            return redirect('groups:group_detail', group_id=group.id)



        messages.error(request, 'إجراء غير معروف.')
        return redirect('groups:group_detail', group_id=group.id)

    now = timezone.now()
    group_sessions = (
        group.live_sessions
        .select_related('instructor')
        .order_by('start_time')
    )
    active_live_sessions = group_sessions.filter(
        start_time__lte=now, end_time__gte=now, is_active=True,
    )
    upcoming_live_sessions = group_sessions.filter(start_time__gt=now)

    # Part 14: آخر 100 رسالة بس (عشان الاستعلام يفضل محدود لو الشات كبر)،
    # مجيبينها بترتيب تنازلي (الأحدث الأول) عشان الـ slice يشتغل صح، وبعدين
    # بنعكسها في بايثون عشان تتعرض في التمبلت من الأقدم للأحدث (شكل شات
    # طبيعي، آخر رسالة في الآخر تحت).
    chat_messages = list(
        group.chat_messages.select_related('sender').order_by('-sent_at')[:100]
    )
    chat_messages.reverse()

    # Part 24: البث المباشر الجديد (GroupLiveSession / LiveKit) — منفصل
    # تمامًا عن active_live_sessions/upcoming_live_sessions فوق (اللي هي
    # workshops.LiveSession القديمة، Google Meet). current_live_session
    # بترجع أول (وعمليًا المفروض تكون الوحيدة) جلسة status='live' للجروب
    # ده دلوقتي، وupcoming_group_live_sessions بترجع الجلسات المجدولة
    # مرتبة بالأقرب أول.
    current_live_session = group.group_live_sessions.filter(status='live').first()
    upcoming_group_live_sessions = list(
        group.group_live_sessions
        .filter(status='scheduled')
        .order_by('scheduled_at')
    )

    context = {
        'group': group,
        'active_subscription': active_subscription,
        'is_owner': is_owner,
        'active_live_sessions': active_live_sessions,
        'upcoming_live_sessions': upcoming_live_sessions,
        'chat_messages': chat_messages,
        'current_live_session': current_live_session,
        'upcoming_group_live_sessions': upcoming_group_live_sessions,
    }

    if is_owner:
        # كل جلسات الجروب (شاملة القديمة/المنتهية) لإدارة المدرس، وقايمة
        # جلساته اللي لسه مش مربوطة بأي جروب عشان يقدر يربطها من هنا.
        context['all_group_sessions'] = list(
            group_sessions.order_by('-start_time')
        )
        context['attachable_sessions'] = list(
            LiveSession.objects.filter(
                instructor=request.user, group__isnull=True,
            ).order_by('-start_time')[:20]
        )
        # Part 26 (نسخة معدّلة — Manual Recording Upload): آخر 5 جلسات
        # GroupLiveSession منتهية للجروب ده — لكل واحدة بنعرض زرار "ارفع
        # التسجيل" (لو recording_file لسه فاضي) أو "شاهد التسجيل" (لو
        # موجود). مقصورة على المدرس صاحب الجروب بس — الطالب أصلاً بيشوف
        # التسجيلات المتاحة من رابط "مكتبة التسجيلات" فوق. الحد بـ [:5]
        # عشان الصفحة متزدحمش لو تراكمت جلسات كتير مع الوقت (نفس فلسفة
        # حد الـ 100 رسالة شات من Part 14).
        context['recent_ended_live_sessions'] = list(
            group.group_live_sessions.filter(status='ended').order_by('-ended_at')[:5]
        )

    return render(request, 'groups/group_detail.html', context)