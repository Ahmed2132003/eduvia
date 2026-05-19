"""
skills_market/views.py
=======================
تم إزالة جميع اعتماديات نظام الاشتراكات والخطط.
الوصول محمي الآن عبر can_access_skills_market (كورس نشط آخر 60 يوم).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

from core.access import can_access_skills_market, ACCESS_DENIED_MESSAGE

from .forms import (
    MessageForm,
    OpportunityApplicationForm,
    OpportunityForm,
    OrderForm,
    ServiceForm,
    SkillForm,
)
from .models import (
    Message,
    Opportunity,
    OpportunityApplication,
    Service,
    ServiceOrder,
    Skill,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _access_denied(request):
    """رد موحَّد عند رفض الوصول."""
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": ACCESS_DENIED_MESSAGE}, status=403)
    messages.error(request, ACCESS_DENIED_MESSAGE)
    return redirect('/')


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@login_required
def skills_list(request):
    """قائمة المهارات - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    query = request.POST.get('search_query', '')
    if query:
        skills = Skill.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        skills = Skill.objects.all()

    return render(request, 'skills_market/skills_list.html', {
        'skills': skills,
        'search_query': query,
    })


@login_required
def add_skill(request):
    """إضافة مهارة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, 'تم إضافة المهارة بنجاح!')
            return redirect('skills_market:skills_list')
    else:
        form = SkillForm()

    return render(request, 'skills_market/add_skill.html', {'form': form})


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

@login_required
def services_list(request):
    """قائمة الخدمات - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    query = request.POST.get('search_query', '')
    skill_id = request.GET.get('skill')
    services = Service.objects.filter(is_active=True)

    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(skill__name__icontains=query)
        )
    if skill_id:
        services = services.filter(skill__id=skill_id)

    return render(request, 'skills_market/services_list.html', {
        'services': services,
        'search_query': query,
    })


@login_required
def add_service(request):
    """إضافة خدمة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    if request.method == 'POST':
        form = ServiceForm(request.POST, user=request.user)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'تم إضافة الخدمة بنجاح!')
            return redirect('skills_market:services_list')
    else:
        form = ServiceForm(user=request.user)

    return render(request, 'skills_market/add_service.html', {'form': form})


@login_required
@transaction.atomic
def order_service(request, service_id, slugified_title):
    """طلب خدمة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    service = get_object_or_404(Service, id=service_id)
    expected_slug = slugify(service.title)
    if slugified_title != expected_slug:
        return redirect('skills_market:order_service',
                        service_id=service_id, slugified_title=expected_slug)

    buyer_profile = getattr(request.user, 'courses_profile', None)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            if buyer_profile and buyer_profile.coins >= service.price_coins:
                if buyer_profile.deduct_coins(service.price_coins):
                    ServiceOrder.objects.create(
                        buyer=request.user,
                        service=service,
                        details=form.cleaned_data['details'],
                        held_coins=service.price_coins,
                    )
                    messages.success(
                        request,
                        f"تم طلب الخدمة '{service.title}' بنجاح!"
                    )
                    return redirect('skills_market:services_list')
                messages.error(request, 'فشل خصم العملات. حاول مرة أخرى.')
            else:
                coins = buyer_profile.coins if buyer_profile else 0
                messages.error(
                    request,
                    f'ليس لديك عملات كافية! لديك {coins} عملة، '
                    f'والخدمة تكلف {service.price_coins} عملة.'
                )
    else:
        form = OrderForm()

    return render(request, 'skills_market/order_service.html', {
        'service': service, 'form': form,
    })


# ---------------------------------------------------------------------------
# Opportunities
# ---------------------------------------------------------------------------

@login_required
def opportunities_list(request):
    """قائمة الفرص - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    opportunities = Opportunity.objects.filter(is_open=True)
    return render(request, 'skills_market/opportunities_list.html', {
        'opportunities': opportunities,
    })


@login_required
def add_opportunity(request):
    """إضافة فرصة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.provider = request.user
            opportunity.save()
            form.save_m2m()
            messages.success(request, 'تم إضافة الفرصة بنجاح!')
            return redirect('skills_market:opportunities_list')
    else:
        form = OpportunityForm()

    return render(request, 'skills_market/add_opportunity.html', {'form': form})


@login_required
def apply_opportunity(request, opportunity_id):
    """التقدم لفرصة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    opportunity = get_object_or_404(Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = OpportunityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.opportunity = opportunity
            application.applicant = request.user
            application.save()
            messages.success(request, 'تم تقديم الطلب بنجاح!')
            return redirect('skills_market:opportunities_list')
    else:
        form = OpportunityApplicationForm()

    return render(request, 'skills_market/apply_opportunity.html', {
        'opportunity': opportunity, 'form': form,
    })


@login_required
def opportunity_applications(request):
    """طلبات الفرص - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    applications = OpportunityApplication.objects.filter(
        opportunity__provider=request.user
    ).order_by('-applied_at')

    return render(request, 'skills_market/opportunity_applications.html', {
        'applications': applications,
    })


@login_required
def application_detail(request, application_id):
    """تفاصيل طلب فرصة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    application = get_object_or_404(OpportunityApplication, id=application_id)

    if application.opportunity.provider != request.user:
        messages.error(request, 'غير مصرح لك بمشاهدة هذا الطلب.')
        return redirect('skills_market:opportunity_applications')

    return render(request, 'skills_market/application_detail.html', {
        'application': application,
    })


@login_required
@transaction.atomic
def accept_application(request, application_id):
    """قبول طلب فرصة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    application = get_object_or_404(
        OpportunityApplication,
        id=application_id,
        opportunity__provider=request.user,
    )

    if application.status != 'accepted':
        application.status = 'accepted'
        order = ServiceOrder.objects.create(
            service=None,
            buyer=application.applicant,
            status='accepted',
            created_at=timezone.now(),
            details=f"فرصة: {application.opportunity.title}",
        )
        application.order = order
        application.save()

        Message.objects.create(
            order=order,
            sender=request.user,
            content=(
                f"لقد تم قبول {application.full_name} في فرصة العمل "
                f"'{application.opportunity.title}' لدينا."
            ),
        )
        Message.objects.create(
            order=order,
            sender=request.user,
            content=(
                f"لقد تم قبولك في فرصة العمل "
                f"'{application.opportunity.title}' لدينا. "
                "سيتم التواصل معك قريبًا."
            ),
        )

        if application.email:
            send_mail(
                'Application Accepted',
                (
                    f'تم قبول طلبك لـ "{application.opportunity.title}". '
                    f'سنتواصل معك قريبًا. '
                    f'التواصل: {application.opportunity.email}'
                ),
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=True,
            )

        messages.success(
            request,
            f"تم قبول طلب {application.full_name}! تم إرسال رسالة وإيميل."
        )
    else:
        messages.warning(request, 'هذا الطلب تم قبوله بالفعل.')

    return redirect('skills_market:opportunity_applications')


# ---------------------------------------------------------------------------
# Messages & Chat
# ---------------------------------------------------------------------------

@login_required
def applicant_messages(request):
    """رسائل المتقدم - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    orders = ServiceOrder.objects.filter(
        buyer=request.user
    ).order_by('-created_at')

    return render(request, 'skills_market/applicant_messages.html', {
        'orders': orders,
    })


@login_required
def applicant_chat(request, order_id):
    """دردشة المتقدم - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    order = get_object_or_404(ServiceOrder, id=order_id)
    messages_list = Message.objects.filter(order=order).order_by('sent_at')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.order = order
            message.save()
            return redirect('skills_market:applicant_chat', order_id=order.id)
    else:
        form = MessageForm()

    return render(request, 'skills_market/applicant_chat.html', {
        'order': order,
        'messages': messages_list,
        'form': form,
    })


@login_required
def track_service(request, order_id):
    """تتبع خدمة - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    order = get_object_or_404(ServiceOrder, id=order_id, buyer=request.user)
    messages_list = order.messages.all().order_by('sent_at')

    if request.method == 'POST':
        if 'complete_service' in request.POST:
            if order.status != 'completed':
                order.status = 'completed'
                order.completed_at = timezone.now()
                if order.service and order.service.provider:
                    seller_profile = getattr(
                        order.service.provider, 'courses_profile', None
                    )
                    if seller_profile:
                        seller_profile.add_coins(order.held_coins)
                order.held_coins = 0
                order.save()
                messages.success(request, 'تم إكمال الخدمة! تم تحويل العملات للمزود.')
            else:
                messages.warning(request, 'الخدمة تم إكمالها بالفعل.')
            return redirect('skills_market:track_service', order_id=order.id)

        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.order = order
            msg.sender = request.user
            msg.save()
            messages.success(request, 'تم إرسال الرسالة بنجاح!')
            return redirect('skills_market:track_service', order_id=order.id)
    else:
        form = MessageForm()

    return render(request, 'skills_market/track_service.html', {
        'order': order,
        'messages': messages_list,
        'form': form,
    })


@login_required
def provider_messages(request):
    """رسائل المزود - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    orders = ServiceOrder.objects.filter(
        service__provider=request.user
    ).order_by('-created_at')

    return render(request, 'skills_market/provider_messages.html', {
        'orders': orders,
    })


@login_required
def provider_chat(request, order_id):
    """دردشة المزود - يتطلب كورسًا نشطًا."""
    if not can_access_skills_market(request.user):
        return _access_denied(request)

    order = get_object_or_404(ServiceOrder, id=order_id)

    if order.service and order.service.provider != request.user:
        messages.error(request, 'غير مصرح لك بمشاهدة هذه الدردشة.')
        return redirect('skills_market:provider_messages')

    messages_list = order.messages.all().order_by('sent_at')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.order = order
            msg.sender = request.user
            msg.save()
            messages.success(request, 'تم إرسال الرسالة بنجاح!')
            return redirect('skills_market:provider_chat', order_id=order.id)
    else:
        form = MessageForm()

    return render(request, 'skills_market/provider_chat.html', {
        'order': order,
        'messages': messages_list,
        'form': form,
    })