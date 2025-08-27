from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BotChat, BotMessage
from django.utils import timezone
from datetime import timedelta
import requests
import os

@login_required
def chatbot_page(request, chat_id=None):
    # إذا كان فيه chat_id، جيب المحادثة
    if chat_id:
        current_chat = BotChat.objects.filter(id=chat_id, user=request.user).first()
        if not current_chat:
            return redirect('chatbot:chatbot_page')
        messages = BotMessage.objects.filter(chat=current_chat).order_by('sent_at')
    else:
        # جيب الـ chat_id من الجلسة لو موجود
        current_chat_id = request.session.get('current_chat_id')
        if current_chat_id:
            current_chat = BotChat.objects.filter(id=current_chat_id, user=request.user).first()
            if current_chat:
                messages = BotMessage.objects.filter(chat=current_chat).order_by('sent_at')
            else:
                current_chat = None
                messages = []
        else:
            current_chat = None
            messages = []

    chats = BotChat.objects.filter(user=request.user).order_by('-created_at')

    # حساب عدد الرسائل اليومية
    today = timezone.now().date()
    daily_message_count = BotMessage.objects.filter(
        chat__user=request.user,
        sent_at__date=today
    ).count()

    # حدود الرسائل بناءً على خطة الاشتراك
    subscription_plan = request.user.profile.subscription_plan
    daily_limit = {
        'free': 5,
        'basic': 30,
        'pro': 60,
        'premium': 100
    }.get(subscription_plan, 5)

    if request.method == 'POST':
        if daily_message_count >= daily_limit:
            return JsonResponse({'redirect': '/accounts/subscribe/'})

        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'})

        # إذا مكنش فيه محادثة حالية، أنشئ واحدة جديدة
        if not current_chat:
            current_chat = BotChat.objects.create(
                user=request.user,
                title=user_message[:50]
            )
            request.session['current_chat_id'] = current_chat.id

        # إرسال الرسالة إلى Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'prompt': user_message}
        response = requests.post('https://api.gemini.com/v1/completions', headers=headers, json=data)

        if response.status_code == 200:
            bot_response = response.json().get('choices', [{}])[0].get('text', 'Sorry, I could not process your request.')
            BotMessage.objects.create(
                chat=current_chat,
                user_message=user_message,
                bot_response=bot_response
            )
            return JsonResponse({
                'response': bot_response,
                'chat_id': current_chat.id,
                'chat_title': current_chat.title
            })
        else:
            return JsonResponse({'error': 'Failed to connect to the chatbot API'})

    context = {
        'chats': chats,
        'current_chat': current_chat,
        'messages': messages,
        'daily_message_count': daily_message_count,
        'daily_limit': daily_limit,
    }
    return render(request, 'chatbot/chatbot.html', context)