from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import LiveSession, LiveRecording
from django.utils.text import slugify
import unicodedata
from courses.models import UserProfile
from datetime import timedelta
from django.contrib import messages

def is_instructor_or_allowed(user):
    if not user.is_authenticated:
        return False
    profile = UserProfile.objects.get(user=user)
    if profile.subscription_plan in ['premium', 'instructor'] or user.role == 'instructor':
        if profile.subscription_plan == 'instructor' and user.role != 'instructor':
            user.role = 'instructor'
            user.save()
        return True
    return user.role == 'instructor'

@login_required(login_url='/')
def live_session_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    current_time = timezone.now()
    active_sessions = LiveSession.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_active=True
    )
    upcoming_sessions = LiveSession.objects.filter(
        start_time__gt=current_time
    ).order_by('start_time')[:5]
    
    user_sessions = None
    if request.user.role == 'instructor':
        user_sessions = LiveSession.objects.filter(instructor=request.user)
    
    # Ensure subscription_plan is correctly set for Instructor Plan
    if profile.subscription_plan == 'instructor' and request.user.role != 'instructor':
        request.user.role = 'instructor'
        request.user.save()
    
    context = {
        'active_sessions': active_sessions,
        'upcoming_sessions': upcoming_sessions,
        'user_sessions': user_sessions,
        'current_time': current_time,
        'subscription_plan': profile.subscription_plan,
        'is_instructor': request.user.role == 'instructor',
    }
    return render(request, 'workshops/live_session_list.html', context)

@login_required(login_url='/')
def watch_live(request, session_id, slugified_title):
    profile = get_object_or_404(UserProfile, user=request.user)
    session = get_object_or_404(LiveSession, id=session_id, is_active=True)

    # Restrict Free plan
    if profile.subscription_plan == 'free':
        messages.error(request, "مشاهدة الجلسات الحية غير متاحة في الخطة المجانية. قم بترقية خطتك!")
        return redirect('workshops:live_session_list')

    # Basic plan: 1 live session per week
    if profile.subscription_plan == 'basic':
        one_week_ago = timezone.now() - timedelta(days=7)
        # Assuming we track views somehow; for simplicity, we'll assume no tracking here, or add a model if needed.
        pass

    if request.user.is_authenticated:
        session.participants.add(request.user)
    return render(request, 'workshops/watch_live.html', {
        'session': session,
        'slugified_title': slugify(unicodedata.normalize('NFKD', session.title or '').encode('ascii', 'ignore').decode('ascii')) or 'no-title'
    })

@login_required(login_url='/')
def watch_recording(request, recording_id, slugified_title):
    profile = get_object_or_404(UserProfile, user=request.user)
    recording = get_object_or_404(LiveRecording, id=recording_id)

    # Restrict Free plan
    if profile.subscription_plan == 'free':
        messages.error(request, "مشاهدة التسجيلات غير متاحة في الخطة المجانية. قم بترقية خطتك!")
        return redirect('workshops:live_session_list')

    # Basic plan: limited views, e.g., 2 per month
    if profile.subscription_plan == 'basic':
        one_month_ago = timezone.now() - timedelta(days=30)
        # Assuming no tracking; add if needed
        pass

    return render(request, 'workshops/watch_recording.html', {
        'recording': recording,
        'slugified_title': slugify(unicodedata.normalize('NFKD', recording.live_session.title or '').encode('ascii', 'ignore').decode('ascii')) or 'no-title'
    })

@login_required(login_url='/')
@user_passes_test(is_instructor_or_allowed, login_url='/')
def create_live_session(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    # Allow access if user has instructor role or correct subscription plan
    if profile.subscription_plan not in ['premium', 'instructor'] and request.user.role != 'instructor':
        messages.error(request, "إنشاء جلسة حية متاح فقط في خطط Premium أو Instructor أو للمستخدمين بدور Instructor.")
        return redirect('workshops:live_session_list')

    # Pro plan: limited sessions, e.g., 2 per month
    if profile.subscription_plan == 'pro':
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_sessions = LiveSession.objects.filter(instructor=request.user, start_time__gte=one_month_ago).count()
        if recent_sessions >= 2:
            messages.error(request, "يمكنك إنشاء جلستين فقط كل شهر في خطة Pro.")
            return redirect('workshops:live_session_list')

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        meet_link = request.POST['meet_link']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        session_image = request.FILES.get('session_image')
        session = LiveSession.objects.create(
            title=title,
            description=description,
            meet_link=meet_link,
            session_image=session_image,
            instructor=request.user,
            start_time=start_time,
            end_time=end_time,
            is_active=False
        )
        slugified_title = slugify(unicodedata.normalize('NFKD', session.title or '').encode('ascii', 'ignore').decode('ascii')) or 'no-title'
        return redirect('workshops:start_live', session_id=session.id, slugified_title=slugified_title)
    return render(request, 'workshops/create_live_session.html')

@login_required(login_url='/')
@user_passes_test(is_instructor_or_allowed, login_url='/')
def start_live(request, session_id, slugified_title):
    profile = get_object_or_404(UserProfile, user=request.user)
    session = get_object_or_404(LiveSession, id=session_id, instructor=request.user, is_active=False)

    if profile.subscription_plan not in ['premium', 'instructor'] and request.user.role != 'instructor':
        messages.error(request, "بدء جلسة حية متاح فقط في خطط Premium أو Instructor أو للمستخدمين بدور Instructor.")
        return redirect('workshops:live_session_list')

    if request.method == 'POST' and timezone.now() >= session.start_time and timezone.now() <= session.end_time:
        session.is_active = True
        session.save()
        return redirect(session.meet_link)
    return render(request, 'workshops/start_live.html', {
        'session': session,
        'slugified_title': slugify(unicodedata.normalize('NFKD', session.title or '').encode('ascii', 'ignore').decode('ascii')) or 'no-title'
    })

@login_required(login_url='/')
@user_passes_test(is_instructor_or_allowed, login_url='/')
def upload_recording(request, session_id, slugified_title):
    profile = get_object_or_404(UserProfile, user=request.user)
    session = get_object_or_404(LiveSession, id=session_id, instructor=request.user)

    if profile.subscription_plan not in ['premium', 'instructor'] and request.user.role != 'instructor':
        messages.error(request, "رفع تسجيل متاح فقط في خطط Premium أو Instructor أو للمستخدمين بدور Instructor.")
        return redirect('workshops:live_session_list')

    if request.method == 'POST':
        video_file = request.POST.get('video_file')
        if video_file:
            try:
                if 'drive.google.com' in video_file and '/view' in video_file:
                    video_file = video_file.replace('/view', '/preview').replace('?usp=sharing', '')
                LiveRecording.objects.create(
                    live_session=session,
                    video_file=video_file
                )
                return redirect('workshops:live_session_list')
            except Exception as e:
                print(f"Error saving recording: {e}")
                return render(request, 'workshops/upload_recording.html', {
                    'session': session,
                    'error': f'Error saving recording: {str(e)}',
                    'slugified_title': slugified_title
                })
        else:
            return render(request, 'workshops/upload_recording.html', {
                'session': session,
                'error': 'Please provide a valid video URL.',
                'slugified_title': slugified_title
            })
    return render(request, 'workshops/upload_recording.html', {
        'session': session,
        'slugified_title': slugify(unicodedata.normalize('NFKD', session.title or '').encode('ascii', 'ignore').decode('ascii')) or 'no-title'
    })