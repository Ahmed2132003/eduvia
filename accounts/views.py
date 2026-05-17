from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from accounts.models import User, Profile
from .forms import RegistrationForm, ProfileForm, MessageForm
from courses.models import UserProfile
from .models import UserChat, UserMessage
from skills_market.models import ServiceOrder

import random
import string
import time
import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Registration & Auth
# ─────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            verification_code = ''.join(random.choices(string.digits, k=6))
            request.session['temp_user_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'role': form.cleaned_data['role'],
                'password': form.cleaned_data['password1'],
                'verification_code': verification_code,
                'code_timestamp': time.time(),
            }
            send_mail(
                'Verify Your Eduvia Account',
                f'Your verification code is: {verification_code}. It will expire in 1 minute.',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            messages.success(
                request,
                'A verification code has been sent to your email. Please enter it within 1 minute.'
            )
            return redirect('accounts:verify_code_form')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_code_form_view(request):
    if 'temp_user_data' not in request.session:
        messages.error(request, 'No registration data found. Please start the registration process again.')
        return redirect('accounts:register')
    return render(request, 'accounts/verify_code.html')


@csrf_protect
def verify_code_view(request):
    if request.method == 'POST':
        if 'temp_user_data' not in request.session:
            messages.error(request, 'No registration data found.')
            return redirect('accounts:register')

        entered_code = request.POST.get('verification_code')
        temp_data = request.session['temp_user_data']

        if time.time() - temp_data['code_timestamp'] > 60:
            del request.session['temp_user_data']
            messages.error(request, 'Verification code has expired.')
            return redirect('accounts:register')

        if entered_code == temp_data['verification_code']:
            try:
                user = User.objects.create_user(
                    username=temp_data['username'],
                    email=temp_data['email'],
                    password=temp_data['password'],
                    role=temp_data['role'],
                )
                Profile.objects.get_or_create(user=user)
                UserProfile.objects.get_or_create(user=user)
                login(request, user)
                del request.session['temp_user_data']
                messages.success(request, 'Registration successful! Your profile has been created.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('accounts:verify_code_form')
        else:
            messages.error(request, 'Invalid verification code.')
            return redirect('accounts:verify_code_form')

    return redirect('accounts:register')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ─────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────

@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = get_object_or_404(Profile, user=user)
    is_own_profile = (user == request.user)

    if not is_own_profile and request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            chat = (
                UserChat.objects.filter(user1=request.user, user2=user).first()
                or UserChat.objects.filter(user1=user, user2=request.user).first()
                or UserChat.objects.create(user1=request.user, user2=user)
            )
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('accounts:profile_view', username=user.username)
    else:
        form = MessageForm()

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'viewed_user': user,
        'is_own_profile': is_own_profile,
        'form': form,
    })


@login_required
def edit_profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            profile.full_name = form.cleaned_data['full_name']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            profile.profile_picture = form.cleaned_data['profile_picture']
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})


# ─────────────────────────────────────────────
# Chat & Messages
# ─────────────────────────────────────────────

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        messages.error(request, "You cannot chat with yourself!")
        return redirect('accounts:profile')

    chat = (
        UserChat.objects.filter(user1=request.user, user2=other_user).first()
        or UserChat.objects.filter(user1=other_user, user2=request.user).first()
        or UserChat.objects.create(user1=request.user, user2=other_user)
    )
    return redirect('accounts:user_chat', chat_id=chat.id)


@login_required
def user_chat(request, chat_id):
    chat = get_object_or_404(UserChat, id=chat_id)
    if request.user not in [chat.user1, chat.user2]:
        messages.error(request, "You do not have permission to access this chat.")
        return redirect('accounts:user_messages')

    messages_list = chat.messages.all().order_by('sent_at')
    other_user = chat.user1 if chat.user2 == request.user else chat.user2

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('accounts:user_chat', chat_id=chat.id)
    else:
        form = MessageForm()

    return render(request, 'accounts/user_chat.html', {
        'chat': chat,
        'other_user': other_user,
        'messages': messages_list,
        'form': form,
    })


@login_required
def user_messages(request):
    chats = UserChat.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-created_at')

    service_orders_as_buyer = ServiceOrder.objects.filter(
        buyer=request.user
    ).order_by('-created_at')

    service_orders_as_provider = ServiceOrder.objects.filter(
        service__provider=request.user
    ).order_by('-created_at')

    chat_data = []
    for chat in chats:
        other_user = chat.user1 if chat.user2 == request.user else chat.user2
        chat_data.append({'chat': chat, 'other_user': other_user.username})

    return render(request, 'accounts/user_messages.html', {
        'chat_data': chat_data,
        'service_orders_as_buyer': service_orders_as_buyer,
        'service_orders_as_provider': service_orders_as_provider,
    })
