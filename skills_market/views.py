from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Skill, Service, ServiceOrder, Opportunity, OpportunityApplication, Message
from .forms import SkillForm, ServiceForm, OrderForm, OpportunityForm, OpportunityApplicationForm, MessageForm
from django.utils.text import slugify
from courses.models import UserProfile
from datetime import timedelta

@login_required
def skills_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    query = request.POST.get('search_query', '')

    # Advanced search only for Premium/Instructor plans
    if query and profile.subscription_plan not in ['premium', 'instructor']:
        messages.error(request, "البحث المتقدم متاح فقط في خطة Premium أو Instructor. قم بترقية خطتك!")
        return redirect('skills_market:skills_list')

    if query:
        skills = Skill.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        skills = Skill.objects.all()

    context = {
        'skills': skills,
        'search_query': query,
        'subscription_plan': profile.subscription_plan,
    }
    return render(request, 'skills_market/skills_list.html', context)

@login_required
def application_detail(request, application_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    application = get_object_or_404(OpportunityApplication, id=application_id)

    # Only allow viewing if user is the provider and has Pro/Premium/Instructor plan
    if application.opportunity.provider != request.user:
        messages.error(request, "غير مصرح لك بمشاهدة هذا الطلب.")
        return redirect('skills_market:opportunity_applications')
    if profile.subscription_plan not in ['pro', 'premium', 'instructor']:
        messages.error(request, "عرض تفاصيل الطلب متاح فقط في خطط Pro، Premium، أو Instructor.")
        return redirect('skills_market:opportunity_applications')

    return render(request, 'skills_market/application_detail.html', {
        'application': application,
    })

@login_required
def add_skill(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    # Restrict Free plan
    if profile.subscription_plan == 'free':
        messages.error(request, "إضافة مهارة غير متاحة في الخطة المجانية. قم بترقية خطتك!")
        return redirect('skills_market:skills_list')

    # Basic plan: 1 skill per month
    if profile.subscription_plan == 'basic':
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_skills = Skill.objects.filter(user=request.user, created_at__gte=one_month_ago).count()
        if recent_skills >= 1:
            messages.error(request, "يمكنك إضافة مهارة واحدة فقط كل شهر في الخطة الأساسية.")
            return redirect('skills_market:skills_list')

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

@login_required
def services_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    query = request.POST.get('search_query', '')
    skill_id = request.GET.get('skill')
    services = Service.objects.all()

    # Advanced search only for Premium/Instructor plans
    if query and profile.subscription_plan not in ['premium', 'instructor']:
        messages.error(request, "البحث المتقدم متاح فقط في خطة Premium أو Instructor.")
        return redirect('skills_market:services_list')

    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(skill__name__icontains=query)
        )
    if skill_id:
        services = services.filter(skill__id=skill_id)

    context = {
        'services': services,
        'search_query': query,
        'subscription_plan': profile.subscription_plan,
    }
    return render(request, 'skills_market/services_list.html', context)

@login_required
def add_service(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    # Restrict Free/Basic plans
    if profile.subscription_plan in ['free', 'basic']:
        messages.error(request, "إضافة خدمة متاحة فقط في خطط Pro، Premium، أو Instructor.")
        return redirect('skills_market:services_list')

    # Pro plan: 5 services per month
    if profile.subscription_plan == 'pro':
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_services = Service.objects.filter(provider=request.user, created_at__gte=one_month_ago).count()
        if recent_services >= 5:
            messages.error(request, "يمكنك إضافة 5 خدمات فقط كل شهر في خطة Pro.")
            return redirect('skills_market:services_list')

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
    profile = get_object_or_404(UserProfile, user=request.user)
    service = get_object_or_404(Service, id=service_id)
    expected_slug = slugify(service.title)
    if slugified_title != expected_slug:
        return redirect('skills_market:order_service', service_id=service_id, slugified_title=expected_slug)

    # Restrict Free plan
    if profile.subscription_plan == 'free':
        messages.error(request, "طلب خدمة غير متاح في الخطة المجانية. قم بترقية خطتك!")
        return redirect('skills_market:services_list')

    # Basic plan: 1 order per week
    if profile.subscription_plan == 'basic':
        one_week_ago = timezone.now() - timedelta(days=7)
        recent_orders = ServiceOrder.objects.filter(buyer=request.user, created_at__gte=one_week_ago).count()
        if recent_orders >= 1:
            messages.error(request, "يمكنك طلب خدمة واحدة فقط كل أسبوع في الخطة الأساسية.")
            return redirect('skills_market:services_list')

    buyer_profile = request.user.courses_profile
    seller_profile = service.provider.courses_profile

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            if buyer_profile.coins >= service.price_coins:
                if buyer_profile.deduct_coins(service.price_coins):
                    order = ServiceOrder.objects.create(
                        buyer=request.user,
                        service=service,
                        details=form.cleaned_data['details'],
                        held_coins=service.price_coins
                    )
                    messages.success(request, f"تم طلب الخدمة '{service.title}' بنجاح! العملات محجوزة حتى اكتمال الخدمة.")
                    return redirect('skills_market:services_list')
                else:
                    messages.error(request, "فشل خصم العملات. حاول مرة أخرى.")
            else:
                messages.error(request, f"ليس لديك عملات كافية! لديك {buyer_profile.coins} عملة، والخدمة تكلف {service.price_coins} عملة.")
    else:
        form = OrderForm()
    return render(request, 'skills_market/order_service.html', {'service': service, 'form': form})

def opportunities_list(request):
    profile = get_object_or_404(UserProfile, user=request.user) if request.user.is_authenticated else None
    opportunities = Opportunity.objects.filter(is_open=True)
    context = {
        'opportunities': opportunities,
        'subscription_plan': profile.subscription_plan if profile else 'free',
    }
    return render(request, 'skills_market/opportunities_list.html', context)

@login_required
def add_opportunity(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    # Restrict to Premium/Instructor plans, activate instructor role for Instructor plan
    if profile.subscription_plan not in ['premium', 'instructor']:
        messages.error(request, "إضافة فرصة متاحة فقط في خطط Premium أو Instructor.")
        return redirect('skills_market:opportunities_list')
    if profile.subscription_plan == 'instructor' and profile.role != 'instructor':
        profile.role = 'instructor'
        profile.save()

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
    profile = get_object_or_404(UserProfile, user=request.user)
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)

    # Restrict Free plan
    if profile.subscription_plan == 'free':
        messages.error(request, "التقدم لفرصة غير متاح في الخطة المجانية. قم بترقية خطتك!")
        return redirect('skills_market:opportunities_list')

    # Basic plan: 1 application per month
    if profile.subscription_plan == 'basic':
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_applications = OpportunityApplication.objects.filter(applicant=request.user, applied_at__gte=one_month_ago).count()
        if recent_applications >= 1:
            messages.error(request, "يمكنك التقدم لفرصة واحدة فقط كل شهر في الخطة الأساسية.")
            return redirect('skills_market:opportunities_list')

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
        'opportunity': opportunity,
        'form': form,
    })

@login_required
def opportunity_applications(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    # Restrict to Pro/Premium/Instructor plans
    if profile.subscription_plan not in ['pro', 'premium', 'instructor']:
        messages.error(request, "عرض طلبات الفرص متاح فقط في خطط Pro، Premium، أو Instructor.")
        return redirect('skills_market:opportunities_list')

    applications = OpportunityApplication.objects.filter(opportunity__provider=request.user).order_by('-applied_at')
    return render(request, 'skills_market/opportunity_applications.html', {'applications': applications})

@login_required
@transaction.atomic
def accept_application(request, application_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    application = get_object_or_404(OpportunityApplication, id=application_id, opportunity__provider=request.user)

    # Restrict to Premium/Instructor plans
    if profile.subscription_plan not in ['premium', 'instructor']:
        messages.error(request, "قبول طلبات الفرص متاح فقط في خطط Premium أو Instructor.")
        return redirect('skills_market:opportunity_applications')

    if application.status != 'accepted':
        application.status = 'accepted'
        order = ServiceOrder.objects.create(
            service=None,
            buyer=application.applicant,
            status='accepted',
            created_at=timezone.now(),
            details=f"فرصة: {application.opportunity.title}"
        )
        application.order = order
        application.save()
        provider_message = Message(
            order=order,
            sender=request.user,
            content=f"لقد تم قبول {application.full_name} في فرصة العمل '{application.opportunity.title}' لدينا."
        )
        provider_message.save()
        applicant_message = Message(
            order=order,
            sender=request.user,
            content=f"لقد تم قبولك في فرصة العمل '{application.opportunity.title}' لدينا. سيتم التواصل معك قريبًا."
        )
        applicant_message.save()
        if application.email:
            send_mail(
                'Application Accepted',
                f'تم قبول طلبك لـ "{application.opportunity.title}". سنتواصل معك قريبًا. التواصل: {application.opportunity.email}',
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=True,
            )
        messages.success(request, f"تم قبول طلب {application.full_name}! تم إرسال رسالة وإيميل.")
    else:
        messages.warning(request, "هذا الطلب تم قبوله بالفعل.")
    return redirect('skills_market:opportunity_applications')

@login_required
def applicant_messages(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = ServiceOrder.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'skills_market/applicant_messages.html', {
        'orders': orders,
        'subscription_plan': profile.subscription_plan,
    })

@login_required
def applicant_chat(request, order_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    order = get_object_or_404(ServiceOrder, id=order_id)

    # Restrict Free/Basic plans from sending messages
    if profile.subscription_plan in ['free', 'basic']:
        messages.error(request, "إرسال الرسائل متاح فقط في خطط Pro، Premium، أو Instructor.")
        return redirect('skills_market:applicant_messages')

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
        'subscription_plan': profile.subscription_plan,
    })

@login_required
def track_service(request, order_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    order = get_object_or_404(ServiceOrder, id=order_id, buyer=request.user)
    messages_list = order.messages.all().order_by('sent_at')

    if request.method == 'POST':
        # Restrict Free/Basic plans from sending messages or completing
        if profile.subscription_plan in ['free', 'basic']:
            messages.error(request, "إرسال الرسائل أو إكمال الخدمة متاح فقط في خطط Pro، Premium، أو Instructor.")
            return redirect('skills_market:track_service', order_id=order.id)

        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.sender = request.user
            message.save()
            messages.success(request, "تم إرسال الرسالة بنجاح!")
            return redirect('skills_market:track_service', order_id=order.id)
        elif 'complete_service' in request.POST and profile.subscription_plan in ['pro', 'premium', 'instructor']:
            if order.status != 'completed':
                order.status = 'completed'
                order.completed_at = timezone.now()
                seller_profile = order.service.provider.courses_profile
                seller_profile.add_coins(order.held_coins)
                order.held_coins = 0
                order.save()
                messages.success(request, "تم إكمال الخدمة! تم تحويل العملات للمزود.")
            else:
                messages.warning(request, "الخدمة تم إكمالها بالفعل.")
            return redirect('skills_market:track_service', order_id=order.id)
    else:
        form = MessageForm()
    return render(request, 'skills_market/track_service.html', {
        'order': order,
        'messages': messages_list,
        'form': form,
        'subscription_plan': profile.subscription_plan,
    })

@login_required
def provider_messages(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = ServiceOrder.objects.filter(service__provider=request.user).order_by('-created_at')
    return render(request, 'skills_market/provider_messages.html', {
        'orders': orders,
        'subscription_plan': profile.subscription_plan,
    })

@login_required
def provider_chat(request, order_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    order = get_object_or_404(ServiceOrder, id=order_id)

    if order.service and order.service.provider != request.user:
        messages.error(request, f"غير مصرح لك بمشاهدة هذه الدردشة. هذا الطلب يخص {order.service.provider.username}.")
        return redirect('skills_market:provider_messages')

    # Restrict Free/Basic plans from sending messages
    if profile.subscription_plan in ['free', 'basic']:
        messages.error(request, "إرسال الرسائل متاح فقط في خطط Pro، Premium، أو Instructor.")
        return redirect('skills_market:provider_messages')

    messages_list = order.messages.all().order_by('sent_at')
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.sender = request.user
            message.save()
            messages.success(request, "تم إرسال الرسالة بنجاح!")
            return redirect('skills_market:provider_chat', order_id=order.id)
    else:
        form = MessageForm()
    return render(request, 'skills_market/provider_chat.html', {
        'order': order,
        'messages': messages_list,
        'form': form,
        'subscription_plan': profile.subscription_plan,
    })