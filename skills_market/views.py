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

@login_required
def skills_list(request):
    query = request.POST.get('search_query', '')
    if query:
        skills = Skill.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        skills = Skill.objects.all()
    
    context = {
        'skills': skills,
        'search_query': query,
    }
    return render(request, 'skills_market/skills_list.html', context)

@login_required
def application_detail(request, application_id):
    application = get_object_or_404(OpportunityApplication, id=application_id)
    if application.opportunity.provider != request.user:
        messages.error(request, "You are not authorized to view this application.")
        return redirect('skills_market:opportunity_applications')
    return render(request, 'skills_market/application_detail.html', {
        'application': application,
    })

@login_required
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('skills_market:skills_list')
    else:
        form = SkillForm()
    return render(request, 'skills_market/add_skill.html', {'form': form})

@login_required
def services_list(request):
    query = request.POST.get('search_query', '')
    skill_id = request.GET.get('skill')
    services = Service.objects.all()

    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(skill__name__icontains=query)
        )
    if skill_id:
        services = services.filter(skill__id=skill_id)

    context = {
        'services': services,
        'search_query': query,
    }
    return render(request, 'skills_market/services_list.html', context)

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, user=request.user)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service added successfully!')
            return redirect('skills_market:services_list')
    else:
        form = ServiceForm(user=request.user)
    return render(request, 'skills_market/add_service.html', {'form': form})

@login_required
@transaction.atomic
def order_service(request, service_id, slugified_title):
    service = get_object_or_404(Service, id=service_id)
    # تحقق اختياري من slugified_title
    expected_slug = slugify(service.title)
    if slugified_title != expected_slug:
        return redirect('skills_market:order_service', service_id=service_id, slugified_title=expected_slug)
    
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
                    messages.success(request, f"Order for '{service.title}' placed successfully! Coins are held until the service is completed.")
                    return redirect('skills_market:services_list')
                else:
                    messages.error(request, "Failed to deduct coins. Please try again.")
            else:
                messages.error(request, f"You do not have enough coins! You have {buyer_profile.coins} coins, but the service costs {service.price_coins} coins.")
    else:
        form = OrderForm()
    return render(request, 'skills_market/order_service.html', {'service': service, 'form': form})

def opportunities_list(request):
    opportunities = Opportunity.objects.filter(is_open=True)
    return render(request, 'skills_market/opportunities_list.html', {'opportunities': opportunities})

@login_required
def add_opportunity(request):
    if request.user.courses_profile.role != 'instructor':
        messages.error(request, 'Only instructors can add opportunities!')
        return redirect('skills_market:opportunities_list')
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.provider = request.user
            opportunity.save()
            form.save_m2m()
            messages.success(request, 'Opportunity added successfully!')
            return redirect('skills_market:opportunities_list')
    else:
        form = OpportunityForm()
    return render(request, 'skills_market/add_opportunity.html', {'form': form})

def apply_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    if request.method == 'POST':
        form = OpportunityApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.opportunity = opportunity
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('skills_market:opportunities_list')
    else:
        form = OpportunityApplicationForm()
    return render(request, 'skills_market/apply_opportunity.html', {
        'opportunity': opportunity,
        'form': form,
    })

@login_required
def opportunity_applications(request):
    applications = OpportunityApplication.objects.filter(opportunity__provider=request.user).order_by('-applied_at')
    return render(request, 'skills_market/opportunity_applications.html', {'applications': applications})

@login_required
@transaction.atomic
def accept_application(request, application_id):
    application = get_object_or_404(OpportunityApplication, id=application_id, opportunity__provider=request.user)
    if application.status != 'accepted':
        application.status = 'accepted'
        order = ServiceOrder.objects.create(
            service=None,
            buyer=application.applicant,
            status='accepted',
            created_at=timezone.now(),
            details=f"Opportunity: {application.opportunity.title}"
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
                f'Your application for "{application.opportunity.title}" has been accepted. We will contact you soon. Contact: {application.opportunity.email}',
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=True,
            )
        messages.success(request, f"Application for {application.full_name} accepted! A message and email have been sent.")
    else:
        messages.warning(request, "This application is already accepted.")
    return redirect('skills_market:opportunity_applications')

@login_required
def applicant_messages(request):
    orders = ServiceOrder.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'skills_market/applicant_messages.html', {'orders': orders})

@login_required
def applicant_chat(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    messages_list = Message.objects.filter(order=order).order_by('sent_at')
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.order = order
            if message.file_url:
                message.file_url = message.file_url
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
    order = get_object_or_404(ServiceOrder, id=order_id, buyer=request.user)
    messages_list = order.messages.all().order_by('sent_at')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('skills_market:track_service', order_id=order.id)
        elif 'complete_service' in request.POST:
            if order.status != 'completed':
                order.status = 'completed'
                order.completed_at = timezone.now()
                seller_profile = order.service.provider.courses_profile
                seller_profile.add_coins(order.held_coins)
                order.held_coins = 0
                order.save()
                messages.success(request, "Service marked as completed! Coins have been transferred to the provider.")
            else:
                messages.warning(request, "Service is already marked as completed.")
            return redirect('skills_market:track_service', order_id=order.id)
    else:
        form = MessageForm()
    return render(request, 'skills_market/track_service.html', {
        'order': order,
        'messages': messages_list,
        'form': form
    })

@login_required
def provider_messages(request):
    orders = ServiceOrder.objects.filter(service__provider=request.user).order_by('-created_at')
    return render(request, 'skills_market/provider_messages.html', {'orders': orders})

@login_required
def provider_chat(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    if order.service and order.service.provider != request.user:
        messages.error(request, f"You are not authorized to view this chat. This order belongs to {order.service.provider.username}.")
        return redirect('skills_market:provider_messages')
    messages_list = order.messages.all().order_by('sent_at')
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('skills_market:provider_chat', order_id=order.id)
    else:
        form = MessageForm()
    return render(request, 'skills_market/provider_chat.html', {
        'order': order,
        'messages': messages_list,
        'form': form
    })