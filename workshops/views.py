from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import LiveSession, LiveRecording

def is_instructor(user):
    return user.is_authenticated and user.role == 'instructor'

@login_required(login_url='/')
def live_session_list(request):
    current_time = timezone.now()  # الوقت الحالي
    active_sessions = LiveSession.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_active=True
    )
    upcoming_sessions = LiveSession.objects.filter(
        start_time__gt=current_time
    ).order_by('start_time')[:5]
    
    user_sessions = None
    if request.user.is_authenticated and request.user.role == 'instructor':
        user_sessions = LiveSession.objects.filter(instructor=request.user)
    
    return render(request, 'workshops/live_session_list.html', {
        'active_sessions': active_sessions,
        'upcoming_sessions': upcoming_sessions,
        'user_sessions': user_sessions,
        'current_time': current_time,  # نمرر الوقت الحالي للقالب
    })

@login_required(login_url='/')
def watch_live(request, session_id):
    session = get_object_or_404(LiveSession, id=session_id, is_active=True)
    if request.user.is_authenticated:
        session.participants.add(request.user)
    return render(request, 'workshops/watch_live.html', {'session': session})

@login_required(login_url='/')
def watch_recording(request, recording_id):
    recording = get_object_or_404(LiveRecording, id=recording_id)
    return render(request, 'workshops/watch_recording.html', {'recording': recording})

@login_required(login_url='/')
@user_passes_test(is_instructor, login_url='/')
def create_live_session(request):
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
        return redirect('workshops:start_live', session_id=session.id)
    return render(request, 'workshops/create_live_session.html')

@login_required(login_url='/')
@user_passes_test(is_instructor, login_url='/')
def start_live(request, session_id):
    session = get_object_or_404(LiveSession, id=session_id, instructor=request.user, is_active=False)
    if request.method == 'POST' and timezone.now() >= session.start_time and timezone.now() <= session.end_time:
        session.is_active = True
        session.save()
        return redirect(session.meet_link)
    return render(request, 'workshops/start_live.html', {'session': session})

@login_required(login_url='/')
@user_passes_test(is_instructor, login_url='/')
def upload_recording(request, session_id):
    session = get_object_or_404(LiveSession, id=session_id, instructor=request.user)
    if request.method == 'POST' and request.FILES.get('video_file'):
        LiveRecording.objects.create(
            live_session=session,
            video_file=request.FILES['video_file']
        )
        return redirect('workshops:live_session_list')
    return render(request, 'workshops/upload_recording.html', {'session': session})