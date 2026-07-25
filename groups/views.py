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

نفس أسلوب الكود المتبع في courses/views.py و workshops/views.py:
function-based views + render + templates (مفيش class-based views).
"""

from decimal import Decimal, ROUND_HALF_UP
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from workshops.models import LiveSession

from .access import is_group_content_accessible, GROUP_FROZEN_MESSAGE
from .forms import PaymentProofForm
from .models import (
    CurriculumCategory,
    GroupCapacityPlan,
    GroupChatMessage,
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
        rows.append({
            'membership': membership,
            'group': group,
            'teacher': group.teacher,
            'category': group.category,
            'is_active': is_active,
            'end_date': active_subscription.end_date if active_subscription else None,
        })

    return render(request, 'groups/my_learning_groups.html', {
        'rows': rows,
    })


# ---------------------------------------------------------------------------
# Part 12/13: Group content page
# ---------------------------------------------------------------------------

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
            content = (request.POST.get('content') or '').strip()
            if content:
                GroupChatMessage.objects.create(
                    group=group,
                    sender=request.user,
                    content=content,
                )
            else:
                messages.error(request, 'اكتب رسالة قبل الإرسال.')
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

    context = {
        'group': group,
        'active_subscription': active_subscription,
        'is_owner': is_owner,
        'active_live_sessions': active_live_sessions,
        'upcoming_live_sessions': upcoming_live_sessions,
        'chat_messages': chat_messages,
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

    return render(request, 'groups/group_detail.html', context)