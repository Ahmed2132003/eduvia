# chatbot/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BotChat, BotMessage
from django.utils import timezone
import requests
import os

from access_control import can_access_chatbot, ACCESS_DENIED_MESSAGE


@login_required
def chatbot_page(request, chat_id=None):
    # ---- التحقق من أهلية المستخدم ----
    if not can_access_chatbot(request.user):
        if request.method == 'POST':
            return JsonResponse(
                {"detail": ACCESS_DENIED_MESSAGE},
                status=403
            )
        return render(request, 'chatbot/chatbot.html', {
            'access_denied': True,
            'access_denied_message': ACCESS_DENIED_MESSAGE,
            'chats': [],
            'current_chat': None,
            'messages': [],
            'daily_message_count': 0,
            'daily_limit': 0,
        })

    # ---- جلب المحادثة الحالية ----
    if chat_id:
        current_chat = BotChat.objects.filter(id=chat_id, user=request.user).first()
        if not current_chat:
            return redirect('chatbot:chatbot_page')
        messages = BotMessage.objects.filter(chat=current_chat).order_by('sent_at')
    else:
        current_chat_id = request.session.get('current_chat_id')
        if current_chat_id:
            current_chat = BotChat.objects.filter(
                id=current_chat_id, user=request.user
            ).first()
            if current_chat:
                messages = BotMessage.objects.filter(chat=current_chat).order_by('sent_at')
            else:
                current_chat = None
                messages = []
        else:
            current_chat = None
            messages = []

    chats = BotChat.objects.filter(user=request.user).order_by('-created_at')

    # ---- حساب عدد الرسائل اليومية (حد ثابت = 20 رسالة/يوم) ----
    today = timezone.now().date()
    daily_message_count = BotMessage.objects.filter(
        chat__user=request.user,
        sent_at__date=today
    ).count()
    daily_limit = 20

    if request.method == 'POST':
        if daily_message_count >= daily_limit:
            return JsonResponse({'error': 'لقد تجاوزت الحد اليومي للرسائل.'}, status=429)

        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'لا يمكن أن تكون الرسالة فارغة.'}, status=400)

        # إنشاء محادثة جديدة إن لم تكن موجودة
        if not current_chat:
            current_chat = BotChat.objects.create(
                user=request.user,
                title=user_message[:50]
            )
            request.session['current_chat_id'] = current_chat.id

        # إرسال الرسالة إلى Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {'prompt': user_message}

        try:
            response = requests.post(
                'https://api.gemini.com/v1/completions',
                headers=headers,
                json=data,
                timeout=15
            )
            if response.status_code == 200:
                bot_response = (
                    response.json()
                    .get('choices', [{}])[0]
                    .get('text', 'عذراً، لم أتمكن من معالجة طلبك.')
                )
            else:
                bot_response = 'عذراً، فشل الاتصال بخدمة الشات بوت.'
        except requests.RequestException:
            bot_response = 'عذراً، حدث خطأ في الاتصال. حاول مجدداً.'

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

    context = {
        'access_denied': False,
        'chats': chats,
        'current_chat': current_chat,
        'messages': messages,
        'daily_message_count': daily_message_count,
        'daily_limit': daily_limit,
    }
    return render(request, 'chatbot/chatbot.html', context)