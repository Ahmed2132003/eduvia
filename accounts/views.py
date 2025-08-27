from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from accounts.models import User ,Profile
from django.contrib import messages
from .forms import RegistrationForm, ProfileForm, MessageForm
from courses.models import UserProfile
from .models import UserChat, UserMessage
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from skills_market.models import ServiceOrder
import random
import string
from django.core.mail import send_mail
from django.conf import settings
import time
from django.views.decorators.csrf import csrf_protect
import paymob
from datetime import datetime, timedelta
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime, timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging
import hmac
import hashlib
paymob.api_key = settings.PAYMOB_API_KEY
logger = logging.getLogger(__name__)

@login_required
def subscribe_view(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')
        duration = request.POST.get('duration')
        phone_number = request.POST.get('phone_number')

        logger.debug(f"Received POST data: plan={plan}, duration={duration}, phone_number={phone_number}")

        if plan not in ['basic', 'pro', 'premium', 'instructor']:
            messages.error(request, 'خطة غير صالحة.')
            logger.error(f"Invalid plan: {plan}")
            return redirect('accounts:subscribe')

        if not phone_number:
            messages.error(request, 'رقم التليفون مطلوب للدفع عبر المحافظ الإلكترونية.')
            logger.error("Phone number is required")
            return redirect('accounts:subscribe')

        prices = {
            'basic': {'monthly': 15000, 'six_months': 81000, 'yearly': 144000},
            'pro': {'monthly': 35000, 'six_months': 189000, 'yearly': 336000},
            'premium': {'monthly': 50000, 'six_months': 270000, 'yearly': 480000},
            'instructor': {'monthly': 40000, 'six_months': 216000, 'yearly': 384000},
        }
        amount = prices[plan][duration]

        try:
            auth_response = requests.post(
                f'{settings.PAYMOB_API_BASE_URL}/auth/tokens',
                json={'api_key': settings.PAYMOB_API_KEY}
            )
            auth_response.raise_for_status()
            auth_token = auth_response.json()['token']
            logger.debug(f"Auth token obtained: {auth_token}")

            order_response = requests.post(
                f'{settings.PAYMOB_API_BASE_URL}/ecommerce/orders',
                json={
                    'auth_token': auth_token,
                    'delivery_needed': False,
                    'amount_cents': amount,
                    'currency': 'EGP',
                    'merchant_order_id': f"{request.user.id}_{plan}_{duration}_{int(datetime.now().timestamp())}"
                }
            )
            order_response.raise_for_status()
            order_id = order_response.json()['id']
            logger.debug(f"Order created: {order_id}")

            payment_key_response = requests.post(
                f'{settings.PAYMOB_API_BASE_URL}/acceptance/payment_keys',
                json={
                    'auth_token': auth_token,
                    'amount_cents': amount,
                    'currency': 'EGP',
                    'order_id': order_id,
                    'billing_data': {
                        'email': request.user.email,
                        'first_name': getattr(request.user.profile, 'full_name', request.user.username) or request.user.username,
                        'phone_number': phone_number,
                        'last_name': 'NA',
                        'street': 'NA',
                        'building': 'NA',
                        'floor': 'NA',
                        'apartment': 'NA',
                        'city': 'NA',
                        'country': 'NA',
                        'postal_code': 'NA',
                        'state': 'NA'
                    },
                    'integration_id': settings.PAYMOB_INTEGRATION_ID
                }
            )
            payment_key_response.raise_for_status()
            payment_key = payment_key_response.json()['token']
            logger.debug(f"Payment key obtained: {payment_key}")

            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.phone_number = phone_number
            profile.paymob_order_id = str(order_id)  
            profile.subscription_duration = duration
            profile.save()
            logger.info(f"Profile updated for user {request.user.id}, order_id {order_id}")

            payment_url = f'{settings.PAYMOB_API_BASE_URL}/acceptance/payments/pay'
            payment_data = {
                'source': {
                    'identifier': phone_number,
                    'subtype': 'WALLET'
                },
                'payment_token': payment_key
            }
            payment_response = requests.post(payment_url, json=payment_data)
            payment_response.raise_for_status()
            redirect_url = payment_response.json().get('redirect_url')
            if not redirect_url:
                raise ValueError("No redirect URL returned from Paymob")
            logger.debug(f"Redirecting to payment URL: {redirect_url}")

            messages.success(request, 'جاري توجيهك لصفحة الدفع...')
            return redirect(redirect_url)

        except (requests.exceptions.RequestException, ValueError) as e:
            messages.error(request, f'خطأ في الدفع: {str(e)}')
            logger.error(f"Payment error: {str(e)}")
            return redirect('accounts:subscribe')

    return render(request, 'accounts/subscribe.html', {})




def verify_hmac(data, secret_key):
    secure_key = secret_key.encode('utf-8')
    ordered_keys = [
        'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction',
        'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded',
        'is_standalone_payment', 'is_voided', 'order', 'owner', 'pending', 'source_data.pan',
        'source_data.sub_type', 'source_data.type', 'success'
    ]
    concatenated_string = ''.join(str(data.get(key, '')) for key in ordered_keys)
    computed_hmac = hmac.new(secure_key, concatenated_string.encode('utf-8'), hashlib.sha512).hexdigest()
    logger.info(f"Computed HMAC: {computed_hmac}, Received HMAC: {data.get('hmac')}")
    return computed_hmac == data.get('hmac')

@csrf_exempt
def payment_callback(request):
    data = request.POST if request.method == 'POST' else request.GET
    logger.debug(f"Callback received: method={request.method}, data={dict(data)}")

    # التحقق من HMAC
    paymob_secret = '1B86912BCE6BBE2BFF095BC2FB1C6702'
    if not verify_hmac(data, paymob_secret):
        logger.error("HMAC verification failed")
        return HttpResponse('Invalid HMAC', status=400)

    if data.get('success') == 'true' and data.get('currency') == 'EGP':
        merchant_order_id = data.get('merchant_order_id')
        try:
            parts = merchant_order_id.split('_')
            if len(parts) < 3:
                raise ValueError(f"Invalid merchant_order_id format: {merchant_order_id}")
            
            user_id, plan, duration = parts[:3]
            
            # جلب المستخدم والبروفايل
            user = get_object_or_404(User, id=user_id)
            profile = get_object_or_404(Profile, user=user)
            user_profile, created = UserProfile.objects.get_or_create(user=user)  # جلب أو إنشاء UserProfile

            # تحديد مدة الاشتراك
            now = datetime.now(timezone.utc)
            if duration == 'yearly':
                new_end_date = now + timedelta(days=365)
            elif duration == 'six_months':
                new_end_date = now + timedelta(days=180)
            elif duration == 'monthly':
                new_end_date = now + timedelta(days=30)
            else:
                raise ValueError(f"Invalid duration: {duration}")

            # تحديث Profile
            profile.subscription_plan = plan
            profile.subscription_duration = duration
            profile.subscription_end_date = new_end_date
            profile.paymob_order_id = data.get('order')
            profile.save()

            # تحديث UserProfile
            user_profile.subscription_plan = plan
            user_profile.subscription_end_date = new_end_date
            user_profile.save()

            logger.info(f"Payment confirmed for user {user_id}, plan {plan}, duration {duration}, end_date {new_end_date}")
            return HttpResponse('Payment confirmed', status=200)
        except (ValueError, User.DoesNotExist, Profile.DoesNotExist) as e:
            logger.error(f"Error processing callback: {str(e)}")
            return HttpResponse(f'Error processing callback: {str(e)}', status=400)
    else:
        logger.warning(f"Payment failed or invalid currency: {data}")
        return HttpResponse('Payment failed or invalid currency', status=400)
    
    
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # إنشاء رمز تحقق عشوائي
            verification_code = ''.join(random.choices(string.digits, k=6))
            # حفظ البيانات مؤقتًا في الجلسة
            request.session['temp_user_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'role': form.cleaned_data['role'],
                'password': form.cleaned_data['password1'],
                'verification_code': verification_code,
                'code_timestamp': time.time()
            }
            # إرسال الرمز إلى البريد الإلكتروني
            send_mail(
                'Verify Your Eduvia Account',
                f'Your verification code is: {verification_code}. It will expire in 1 minute.',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            messages.success(request, 'A verification code has been sent to your email. Please enter it within 1 minute.')
            return redirect('accounts:verify_code_form')  # Redirect to a new verification page
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


from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Profile
from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def verify_code_view(request):
    if request.method == 'POST':
        if 'temp_user_data' in request.session:
            entered_code = request.POST.get('verification_code')
            temp_data = request.session['temp_user_data']
            current_time = time.time()
            if current_time - temp_data['code_timestamp'] > 60:
                del request.session['temp_user_data']
                messages.error(request, 'Verification code has expired.')
                return redirect('accounts:register')
            if entered_code == temp_data['verification_code']:
                try:
                    user = User.objects.create_user(
                        username=temp_data['username'],
                        email=temp_data['email'],
                        password=temp_data['password'],
                        role=temp_data['role']
                    )
                    Profile.objects.get_or_create(user=user)
                    UserProfile.objects.get_or_create(user=user)  # إنشاء UserProfile
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
        else:
            messages.error(request, 'No registration data found.')
            return redirect('accounts:register')
    return redirect('accounts:register')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import User, Profile
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            Profile.objects.get_or_create(user=user)  # إنشاء Profile فقط
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')
def logout_view(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Profile 
from .forms import MessageForm

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
            chat = UserChat.objects.filter(user1=request.user, user2=user).first()
            if not chat:
                chat = UserChat.objects.filter(user1=user, user2=request.user).first()
            if not chat:
                chat = UserChat.objects.create(user1=request.user, user2=user)
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
        'form': form
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from courses.models import UserProfile
from .forms import ProfileForm

@login_required
def edit_profile_view(request):
    # جيب أو أنشئ UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # جيب أو أنشئ Profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # احفظ UserProfile
            user_profile = form.save()
            # حدّث حقول Profile بنفس البيانات
            profile.full_name = form.cleaned_data['full_name']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            profile.profile_picture = form.cleaned_data['profile_picture']  # حفظ رابط URL
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=user_profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        messages.error(request, "You cannot chat with yourself!")
        return redirect('accounts:profile')
    chat = UserChat.objects.filter(user1=request.user, user2=other_user).first()
    if not chat:
        chat = UserChat.objects.filter(user1=other_user, user2=request.user).first()
    if not chat:
        chat = UserChat.objects.create(user1=request.user, user2=other_user)
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
        'form': form
    })

@login_required
def user_messages(request):
    chats = UserChat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-created_at')
    service_orders_as_buyer = ServiceOrder.objects.filter(buyer=request.user).order_by('-created_at')
    service_orders_as_provider = ServiceOrder.objects.filter(service__provider=request.user).order_by('-created_at')
    chat_data = []
    for chat in chats:
        other_user = chat.user1 if chat.user2 == request.user else chat.user2
        chat_data.append({
            'chat': chat,
            'other_user': other_user.username
        })
    return render(request, 'accounts/user_messages.html', {
        'chat_data': chat_data,
        'service_orders_as_buyer': service_orders_as_buyer,
        'service_orders_as_provider': service_orders_as_provider
    })