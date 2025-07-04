from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django import forms
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Max
from .models import Course, Video, UserProfile, CourseEnrollment, VideoFile, Comment, VideoRating, Certificate, VideoProgress, UserTaskSubmission, AlternativeQuiz, Task
from .forms import AlternativeQuizForm, TaskForm
from .decorators import instructor_required
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from django.conf import settings
import re

User = get_user_model()

# دالة لتنظيف النصوص من الأحرف غير المرغوب فيها
def clean_text(text):
    return re.sub(r'[^\x20-\x7E]', ' ', text).strip()

# تنزيل الشهادة
@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)

    if not enrollment.is_course_completed():
        messages.error(request, 'You must complete all videos to download the certificate.')
        return redirect('courses:course_details', course_id=course.id)

    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'certificate_number': str(uuid.uuid4())}
    )

    if not enrollment.certificate_issued:
        enrollment.certificate_issued = True
        enrollment.save()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=1*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontName='Times-Roman', fontSize=32, textColor=colors.navy, alignment=1, spaceAfter=20, leading=36)
    subtitle_style = ParagraphStyle(name='Subtitle', fontName='Times-Roman', fontSize=20, textColor=colors.white, alignment=1, spaceAfter=15, leading=24)
    body_style = ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=16, textColor=colors.white, alignment=1, spaceAfter=12, leading=20)
    stamp_style = ParagraphStyle(name='Stamp', fontName='Times-Roman', fontSize=14, textColor=colors.navy, alignment=1, spaceAfter=8, leading=16)
    signature_style = ParagraphStyle(name='Signature', fontName='Times-Italic', fontSize=12, textColor=colors.navy, alignment=1, spaceAfter=12, leading=14)

    course_title = clean_text(course.title)
    try:
        full_name = clean_text(request.user.profile.full_name or request.user.username)
    except UserProfile.DoesNotExist:
        print(f"Profile not found for user: {request.user.username}")
        full_name = clean_text(request.user.username)
    instructor = clean_text(course.instructor)

    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo_eduvia1.png')
    company_logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'creativity_code.png')
    logo_table_data = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([logo])
    else:
        print(f"Error: Eduvia logo not found at {logo_path}. Please place 'logo_eduvia1.jpg' in 'Eduvia/static/images/' and run 'python manage.py collectstatic'.")
        logo_table_data.append([Paragraph("Eduvia Logo", body_style)])
    if os.path.exists(company_logo_path):
        company_logo = Image(company_logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([company_logo])
    else:
        print(f"Error: Company logo not found at {company_logo_path}. Please place 'creativity_code.jpg' in 'Eduvia/static/images/' and run 'python manage.py collectstatic'.")
        logo_table_data.append([Paragraph("Creativity Code Logo", body_style)])

    logo_table = Table([[logo_table_data[0][0], '', logo_table_data[1][0]]], colWidths=[2*inch, 4*inch, 2*inch])
    logo_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (0,0), 'LEFT'), ('ALIGN', (-1,-1), (-1,-1), 'RIGHT')]))
    elements.append(logo_table)
    elements.append(Spacer(1, 0.3*inch))

    elements.append(Paragraph("Certificate of Completion", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Eduvia", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"This certificate is proudly presented to <b>{full_name}</b> for successfully completing the course", body_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>{course_title}</b>", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Instructed by: {instructor}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Congratulations on your dedication and achievement! Keep learning and shining!", body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Certificate Number: {certificate.certificate_number}", body_style))
    elements.append(Paragraph(f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}", body_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Certified by: Eduvia", stamp_style))
    elements.append(Paragraph("Eng. Ahmed Ibrahim", signature_style))

    def draw_border_and_background(canvas, doc):
        canvas.saveState()
        canvas.linearGradient(0, 0, A4[0], A4[1], [colors.cyan, colors.lightcyan])
        canvas.setStrokeColor(colors.navy)
        canvas.setLineWidth(6)
        canvas.rect(0.25*inch, 0.25*inch, A4[0]-0.5*inch, A4[1]-0.5*inch, fill=0, stroke=1)
        canvas.setStrokeColor(colors.white)
        canvas.setLineWidth(2)
        canvas.rect(0.35*inch, 0.35*inch, A4[0]-0.7*inch, A4[1]-0.7*inch, fill=0, stroke=1)
        canvas.setStrokeColor(colors.navy)
        canvas.setLineWidth(1)
        canvas.line(0.25*inch, A4[1]-0.75*inch, 0.25*inch, A4[1]-0.25*inch)
        canvas.line(0.25*inch, A4[1]-0.25*inch, 0.75*inch, A4[1]-0.25*inch)
        canvas.line(A4[0]-0.75*inch, A4[1]-0.25*inch, A4[0]-0.25*inch, A4[1]-0.25*inch)
        canvas.line(A4[0]-0.25*inch, A4[1]-0.75*inch, A4[0]-0.25*inch, A4[1]-0.25*inch)
        canvas.line(0.25*inch, 0.25*inch, 0.25*inch, 0.75*inch)
        canvas.line(0.25*inch, 0.25*inch, 0.75*inch, 0.25*inch)
        canvas.line(A4[0]-0.75*inch, 0.25*inch, A4[0]-0.25*inch, 0.25*inch)
        canvas.line(A4[0]-0.25*inch, 0.25*inch, A4[0]-0.25*inch, 0.75*inch)

    doc.build(elements, onFirstPage=draw_border_and_background, onLaterPages=draw_border_and_background)
    buffer.seek(0)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{course_title}_{request.user.username}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response

# Form for creating/updating courses
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(choices=Course.CATEGORY_CHOICES),
        }

# Form for creating/updating videos
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_url', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Course, Video

def instructor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'courses_profile') or request.user.courses_profile.role != 'instructor':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@instructor_required
def instructor_dashboard(request):
    # جلب الكورسات الخاصة بالمدرب الحالي بناءً على username
    courses = Course.objects.filter(instructor=request.user.username)
    # جلب الفيديوهات لكل كورس وتخزينها كقائمة منفصلة
    for course in courses:
        course.video_list = Video.objects.filter(course=course).order_by('order')
    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'total_videos': Video.objects.filter(course__in=courses).count(),
    }
    return render(request, 'courses/dashboard.html', context)

# Add new course
# courses/views.py
@login_required
@instructor_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)  # إزالة request.FILES
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user.username
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    return render(request, 'courses/add_course.html', {'form': form})
# Edit existing course
# courses/views.py
@login_required
@instructor_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)  # إزالة request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})



import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import instructor_required
from .forms import VideoForm
from .models import Course, Video

@login_required
@instructor_required
def add_video(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    if request.method == 'POST':
        form = VideoForm(request.POST)  # لم نعد نحتاج request.FILES
        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()
            logger.debug(f"Video saved with ID: {video.id}")
            messages.success(request, 'Video added successfully!')
            return redirect('courses:watch_video', course_id=course.id, video_id=video.id)
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = VideoForm()
    return render(request, 'courses/add_video.html', {'form': form, 'course': course})

# View all videos for a course
@login_required
@instructor_required
def course_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    videos = course.videos.all()
    return render(request, 'courses/course_videos.html', {'course': course, 'videos': videos})

# Edit existing video
@login_required
@instructor_required
def edit_video(request, course_id, video_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    video = get_object_or_404(Video, id=video_id, course=course)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated successfully!')
            return redirect('courses:course_videos', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VideoForm(instance=video)
    return render(request, 'courses/edit_video.html', {'form': form, 'course': course, 'video': video})

# List all courses
def courses_view(request):
    courses = Course.objects.all()
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(CourseEnrollment.objects.filter(user=request.user).values_list('course__id', flat=True))
        print(f"User: {request.user.username}, Enrolled course IDs: {enrolled_course_ids}")
    return render(request, 'courses/courses.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids
    })

# Enroll in a course
@login_required
def enroll_course(request, course_id):
    if request.method != 'POST':
        print(f"Invalid request method for course ID: {course_id}")
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    course = get_object_or_404(Course, id=course_id)
    try:
        user_profile = request.user.courses_profile
    except UserProfile.DoesNotExist:
        print(f"Error: UserProfile not found for user {request.user.username}")
        return JsonResponse({'success': False, 'message': 'User profile not found. Please contact support.'}, status=400)

    print(f"User: {request.user.username}, Coins: {user_profile.coins}, Course ID: {course_id}")

    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        print(f"User {request.user.username} already enrolled in course {course_id}")
        return JsonResponse({
            'success': True,
            'message': 'You are already enrolled in this course.',
            'redirect': f'/courses/details/{course.id}/',
            'coins': user_profile.coins
        })

    required_coins = 300
    if user_profile.coins < required_coins:
        print(f"Insufficient coins: Available {user_profile.coins}, Required {required_coins}")
        return JsonResponse({'success': False, 'message': f'You need {required_coins} coins to purchase this course. You have {user_profile.coins} coins.'}, status=400)

    try:
        if not user_profile.deduct_coins(required_coins):
            print(f"Failed to deduct coins: Insufficient balance")
            return JsonResponse({'success': False, 'message': 'Failed to deduct coins. Insufficient balance.'}, status=400)
        CourseEnrollment.objects.create(user=request.user, course=course)
        print(f"Enrollment successful! Coins after deduction: {user_profile.coins}")
        return JsonResponse({
            'success': True,
            'message': 'Course purchased successfully!',
            'new_coins': user_profile.coins,
            'redirect': f'/courses/details/{course.id}/'
        })
    except Exception as e:
        print(f"Error during enrollment: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Failed to purchase course: {str(e)}'}, status=500)

# Check enrollment status
@login_required
def check_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    return JsonResponse({'is_enrolled': is_enrolled})

# Course details with videos
@login_required
def course_details_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    
    if not is_enrolled:
        messages.error(request, 'You must purchase this course to view its details.')
        return redirect('courses:courses')

    videos = course.videos.all()
    if videos.exists() and not videos.first().unlocked:
        first_video = videos.first()
        first_video.unlocked = True
        first_video.save()

    completed_videos_count = 0
    total_videos_count = videos.count()
    if request.user.is_authenticated:
        completed_videos_count = VideoProgress.objects.filter(user=request.user, video__course=course, completed=True).count()

    context = {
        "course": course,
        "videos": videos,
        "is_enrolled": is_enrolled,
        "completed_videos_count": completed_videos_count,
        "total_videos_count": total_videos_count,
    }
    return render(request, 'courses/course_details.html', context)

# Watch video with task handling
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import Course, Video, VideoProgress, CourseEnrollment, Task, AlternativeQuiz, UserTaskSubmission, VideoRating
from .decorators import instructor_required

from .models import VideoFile  # تأكد من استيراد نموذج VideoFile

@login_required
def watch_video(request, course_id, video_id):
    course = get_object_or_404(Course, id=course_id)
    video = get_object_or_404(Video, id=video_id, course=course)
    
    if not CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'يجب شراء هذه الدورة لمشاهدة الفيديوهات.')
        return redirect('courses:courses')

    videos = course.videos.order_by('order')
    video_progress, created = VideoProgress.objects.get_or_create(
        user=request.user,
        video=video,
        defaults={'completed': False, 'progress_percentage': 0.0, 'current_time': 0.0}
    )

    tasks = Task.objects.filter(video=video)
    alternative_quiz = AlternativeQuiz.objects.filter(video=video).first()
    submissions = UserTaskSubmission.objects.filter(user=request.user, task__video=video)
    task_submissions = {sub.task_id: sub for sub in submissions}

    last_submission = submissions.order_by('-attempt_number').first()
    show_main_task = True
    show_alternative_quiz = False

    if last_submission:
        correct_count = sum(1 for c in last_submission.is_correct if c)
        total_questions = len(tasks.first().questions) if tasks.exists() else 1
        success_rate = (correct_count / total_questions) * 100
        if success_rate < 50:
            show_main_task = False
            show_alternative_quiz = True
        elif success_rate >= 50 and not video_progress.completed:
            video_progress.completed = True
            video_progress.save()
            try:
                user_profile = request.user.courses_profile
                user_profile.add_coins(50)
                messages.success(request, f'تم إكمال الفيديو! لقد حصلت على 50 نقطة. نسبة نجاحك: {success_rate:.0f}%')
            except UserProfile.DoesNotExist:
                messages.error(request, 'خطأ: لم يتم العثور على ملف المستخدم.')

    # معالجة رفع الملف
    if request.method == 'POST' and 'upload_file' in request.POST:
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        if not file:
            messages.error(request, 'يرجى اختيار ملف للرفع.')
            return redirect('courses:watch_video', course_id=course.id, video_id=video.id)

        try:
            # إنشاء سجل جديد للملف المرفوع
            video_file = VideoFile(
                video=video,
                user=request.user,
                file=file,
                description=description,
                is_instructor_upload=(request.user.courses_profile.role == 'instructor')
            )
            video_file.save()
            messages.success(request, 'تم رفع الملف بنجاح!')
        except Exception as e:
            messages.error(request, f'فشل رفع الملف: {str(e)}')
        
        return redirect('courses:watch_video', course_id=course.id, video_id=video.id)

    # معالجة إرسال المهمة
    if request.method == 'POST' and 'submit_task' in request.POST:
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, video=video)
        submitted_answers = request.POST.getlist('answers[]')

        if len(submitted_answers) != len(task.questions):
            messages.error(request, 'يجب الإجابة على جميع الأسئلة.')
            return redirect('courses:watch_video', course_id=course.id, video_id=video.id)

        max_attempt = UserTaskSubmission.objects.filter(user=request.user, task=task).aggregate(Max('attempt_number'))['attempt_number__max'] or 0
        new_attempt = max_attempt + 1

        is_correct = [ans == q['correct_answer'] for ans, q in zip(submitted_answers, task.questions)]
        correct_count = sum(1 for c in is_correct if c)
        success_rate = (correct_count / len(task.questions)) * 100

        UserTaskSubmission.objects.update_or_create(
            user=request.user,
            task=task,
            attempt_number=new_attempt,
            defaults={'submitted_answers': submitted_answers, 'is_correct': is_correct}
        )

        if success_rate >= 50 and not video_progress.completed:
            video_progress.completed = True
            video_progress.save()
            try:
                user_profile = request.user.courses_profile
                user_profile.add_coins(50)
                messages.success(request, f'تم إكمال الفيديو! لقد حصلت على 50 نقطة. نسبة نجاحك: {success_rate:.0f}%')
            except UserProfile.DoesNotExist:
                messages.error(request, 'خطأ: لم يتم العثور على ملف المستخدم.')
        else:
            show_main_task = False
            show_alternative_quiz = True
            messages.info(request, f'نسبة نجاحك: {success_rate:.0f}%. تحتاج إلى 50% للنجاح. الاختبار البديل متاح الآن.')

        return redirect('courses:watch_video', course_id=course.id, video_id=video.id)

    # معالجة إرسال الاختبار البديل
    if request.method == 'POST' and 'submit_alternative_quiz' in request.POST:
        quiz_id = request.POST.get('quiz_id')
        submitted_answer = request.POST.get('answer')
        quiz = get_object_or_404(AlternativeQuiz, id=quiz_id, video=video)

        if submitted_answer == quiz.correct_answer:
            task = tasks.first()
            max_attempt = UserTaskSubmission.objects.filter(user=request.user, task=task).aggregate(Max('attempt_number'))['attempt_number__max'] or 0
            UserTaskSubmission.objects.update_or_create(
                user=request.user,
                task=task,
                attempt_number=max_attempt + 1,
                defaults={'submitted_answers': [submitted_answer], 'is_correct': [True]}
            )
            quiz.used = True
            quiz.save()
            video_progress.completed = True
            video_progress.save()
            try:
                user_profile = request.user.courses_profile
                user_profile.add_coins(50)
                messages.success(request, 'تم اجتياز الاختبار البديل! تم إكمال الفيديو. لقد حصلت على 50 نقطة.')
            except UserProfile.DoesNotExist:
                pass
        else:
            quiz.used = False
            quiz.save()
            show_main_task = True
            show_alternative_quiz = False
            messages.error(request, 'إجابة غير صحيحة. يمكنك إعادة محاولة المهمة الرئيسية.')

        return redirect('courses:watch_video', course_id=course.id, video_id=video.id)

    if video_progress.completed:
        next_video = videos.filter(order__gt=video.order).first()
        if next_video and not next_video.unlocked:
            next_video.unlocked = True
            next_video.save()

    completed_videos_count = VideoProgress.objects.filter(user=request.user, video__course=course, completed=True).count()
    total_videos_count = videos.count()

    uploaded_files = video.files.all()
    user_rating = VideoRating.objects.filter(video=video, user=request.user).first()
    user_rating = user_rating.rating if user_rating else None

    context = {
        'course': course,
        'video': video,
        'completed_videos_count': completed_videos_count,
        'total_videos_count': total_videos_count,
        'uploaded_files': uploaded_files,
        'video_progress': video_progress,
        'user_rating': user_rating,
        'tasks': tasks,
        'task_submissions': task_submissions,
        'alternative_quiz': alternative_quiz,
        'show_main_task': show_main_task,
        'show_alternative_quiz': show_alternative_quiz,
    }
    return render(request, 'courses/watch_video.html', context)

# Get rating
def get_rating(request, video_id):
    if not request.user.is_authenticated:
        return JsonResponse({'rating': None})
    rating = VideoRating.objects.filter(video_id=video_id, user=request.user).first()
    return JsonResponse({'rating': rating.rating if rating else None})

# Rate a video
@login_required
def rate_video(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        rating = int(request.POST.get('rating', 0))
        VideoRating.objects.update_or_create(video=video, user=request.user, defaults={'rating': rating})
        return redirect('courses:watch_video', course_id=video.course.id, video_id=video.id)

# Add a comment to a video
@login_required
def add_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(video=video, user=request.user, content=content)
    return redirect('courses:watch_video', course_id=video.course.id, video_id=video.id)

# Update progress
@login_required
def update_progress(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        current_time = float(request.POST.get('current_time', 0.0))
        video_progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'completed': False, 'progress_percentage': 0.0, 'current_time': 0.0}
        )
        video_progress.current_time = current_time
        duration = video.get_duration()
        if duration:
            video_progress.progress_percentage = (current_time / duration) * 100
            if current_time >= duration - 1:
                video_progress.completed = True
                video_progress.save()
                try:
                    user_profile = request.user.courses_profile
                    user_profile.add_coins(50)
                except UserProfile.DoesNotExist:
                    pass
        video_progress.save()
        return JsonResponse({'progress': video_progress.progress_percentage, 'completed': video_progress.completed})
    progress = video_progress.progress_percentage if hasattr(video_progress, 'progress_percentage') else 0
    return JsonResponse({'progress': progress})

# Search for courses
def search_courses(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(title__icontains=query) | Course.objects.filter(description__icontains=query) | Course.objects.filter(category__icontains=query) if query else Course.objects.none()

    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(CourseEnrollment.objects.filter(user=request.user).values_list('course__id', flat=True))
        print(f"User: {request.user.username}, Enrolled course IDs: {enrolled_course_ids}")

    return render(request, 'courses/search_results.html', {
        'query': query,
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids
    })

@login_required
@instructor_required
def add_task(request, course_id, video_id):
    video = get_object_or_404(Video, id=video_id, course__id=course_id, course__instructor=request.user.username)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.video = video
            task.questions = form.cleaned_data['questions_json']
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('courses:course_videos', course_id=course_id)
    else:
        form = TaskForm()
    return render(request, 'courses/add_task.html', {'form': form, 'video': video})

@login_required
@instructor_required
def add_alternative_quiz(request, course_id, video_id):
    video = get_object_or_404(Video, id=video_id, course__id=course_id, course__instructor=request.user.username)
    if request.method == 'POST':
        form = AlternativeQuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.video = video
            quiz.save()
            messages.success(request, 'Alternative quiz added successfully!')
            return redirect('courses:course_videos', course_id=course_id)
    else:
        form = AlternativeQuizForm()
    return render(request, 'courses/add_alternative_quiz.html', {'form': form, 'video': video})