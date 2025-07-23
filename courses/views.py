from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponsePermanentRedirect
from django.urls import reverse
from django import forms
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.core.exceptions import PermissionDenied
from .models import Course, Video, UserProfile, CourseEnrollment, VideoFile, Comment, VideoRating, Certificate, VideoProgress, UserTaskSubmission, AlternativeQuiz, Task
from .forms import AlternativeQuizForm, TaskForm
from .decorators import instructor_required
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import os
from django.conf import settings
import re
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def clean_text(text):
    """تنظيف النص من الأحرف غير المدعومة مع دعم الأحرف العربية"""
    if not text or not text.strip():
        return 'default-title'
    # السماح بالأحرف العربية، الإنجليزية، الأرقام، المسافات، والشرطات
    text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', text).strip()
    cleaned = text if text else 'default-title'
    slugified = slugify(cleaned, allow_unicode=True)
    return slugified if slugified else 'default-title'

def redirect_old_course_url(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    return HttpResponsePermanentRedirect(reverse('courses:course_details', kwargs={
        'course_id': course.id,
        'course_title': slugified_title
    }))

def redirect_old_video_url(request, course_id, video_id):
    video = get_object_or_404(Video, id=video_id, course__id=course_id)
    cleaned_course_title = clean_text(video.course.title)
    cleaned_video_title = clean_text(video.title)
    return HttpResponsePermanentRedirect(reverse('courses:watch_video', kwargs={
        'course_id': course_id,
        'course_title': slugify(cleaned_course_title, allow_unicode=True) or 'default-title',
        'video_id': video_id,
        'video_title': slugify(cleaned_video_title, allow_unicode=True) or 'default-title'
    }))

@login_required
def download_certificate(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Download Certificate - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:download_certificate', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)
    if not enrollment.is_course_completed():
        messages.error(request, 'You must complete all videos to download the certificate.')
        return redirect('courses:course_details', course_id=course.id, course_title=slugified_title)

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

    course_title_cleaned = clean_text(course.title)
    try:
        full_name = clean_text(request.user.courses_profile.full_name or request.user.username)
    except UserProfile.DoesNotExist:
        full_name = clean_text(request.user.username)
    instructor = clean_text(course.instructor)

    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo_eduvia1.png')
    company_logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'creativity_code.png')
    logo_table_data = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([logo])
    else:
        logo_table_data.append([Paragraph("Eduvia Logo", body_style)])
    if os.path.exists(company_logo_path):
        company_logo = Image(company_logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([company_logo])
    else:
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
    elements.append(Paragraph(f"<b>{course_title_cleaned}</b>", subtitle_style))
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
    response['Content-Disposition'] = f'attachment; filename="certificate_{course_title_cleaned}_{request.user.username}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(choices=Course.CATEGORY_CHOICES),
            'image': forms.URLInput(attrs={'placeholder': 'Enter image URL (e.g., Google Drive link)'}),
        }
        labels = {
            'title': 'Course Title',
            'description': 'Description',
            'category': 'Category',
            'image': 'Image URL',
        }

    def clean_image(self):
        image_url = self.cleaned_data.get('image')
        if image_url:
            if not image_url.startswith(('http://', 'https://')):
                raise forms.ValidationError("Please enter a valid URL starting with http:// or https://")
        return image_url

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_url', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter video description'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Enter video URL (e.g., Google Drive link)'}),
            'order': forms.NumberInput(attrs={'placeholder': 'Enter video order'}),
        }
        labels = {
            'title': 'Video Title',
            'description': 'Description',
            'video_url': 'Video URL',
            'order': 'Order',
        }

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        if not video_url:
            raise forms.ValidationError("يجب إدخال رابط فيديو.")
        return cleaned_data

@login_required
@instructor_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user.username)
    for course in courses:
        course.video_list = Video.objects.filter(course=course).order_by('order')
    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'total_videos': Video.objects.filter(course__in=courses).count(),
    }
    return render(request, 'courses/dashboard.html', context)

@login_required
@instructor_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
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

@login_required
@instructor_required
def edit_course(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Edit Course - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:edit_course', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})

@login_required
@instructor_required
def add_video(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Video - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_video', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()
            messages.success(request, 'Video added successfully!')
            return redirect('courses:watch_video', course_id=course.id, course_title=slugified_title, video_id=video.id, video_title=slugify(clean_text(video.title), allow_unicode=True) or 'default-title')
        else:
            messages.error(request, 'Please correct the errors below.')
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = VideoForm()
    return render(request, 'courses/add_video.html', {'form': form, 'course': course})

@login_required
@instructor_required
def course_videos(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Course Videos - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:course_videos', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    videos = course.videos.all()
    return render(request, 'courses/course_videos.html', {'course': course, 'videos': videos})

@login_required
@instructor_required
def edit_video(request, course_id, course_title, video_id, video_title):
    course = get_object_or_404(Course, id=course_id, instructor=request.user.username)
    cleaned_course_title = clean_text(course.title)
    slugified_course_title = slugify(cleaned_course_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Edit Video - Course ID: {course_id}, Original Course Title: {course.title}, Cleaned Course Title: {cleaned_course_title}, Slugified Course Title: {slugified_course_title}, Received Course Title: {course_title}")
    
    if slugified_course_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:edit_video', kwargs={'course_id': course_id, 'course_title': slugified_course_title, 'video_id': video_id, 'video_title': video_title}))
    
    video = get_object_or_404(Video, id=video_id, course=course)
    cleaned_video_title = clean_text(video.title)
    slugified_video_title = slugify(cleaned_video_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Edit Video - Video ID: {video_id}, Original Video Title: {video.title}, Cleaned Video Title: {cleaned_video_title}, Slugified Video Title: {slugified_video_title}, Received Video Title: {video_title}")
    
    if slugified_video_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:edit_video', kwargs={'course_id': course_id, 'course_title': slugified_course_title, 'video_id': video_id, 'video_title': slugified_video_title}))
    
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated successfully!')
            return redirect('courses:course_videos', course_id=course.id, course_title=slugified_course_title)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VideoForm(instance=video)
    return render(request, 'courses/edit_video.html', {'form': form, 'course': course, 'video': video})

def courses_view(request):
    courses = Course.objects.all()
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(CourseEnrollment.objects.filter(user=request.user).values_list('course__id', flat=True))
    for course in courses:
        logger.debug(f"Courses View - Course ID: {course.id}, Title: {course.title}, Slugified: {slugify(clean_text(course.title), allow_unicode=True)}")
    return render(request, 'courses/courses.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids
    })

@login_required
def enroll_course(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Enroll Course - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:enroll_course', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        user_profile = request.user.courses_profile
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found. Please contact support.'}, status=400)

    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        return JsonResponse({
            'success': True,
            'message': 'You are already enrolled in this course.',
            'redirect': reverse('courses:course_details', kwargs={'course_id': course.id, 'course_title': slugified_title}),
            'coins': user_profile.coins
        })

    required_coins = 300
    if user_profile.coins < required_coins:
        return JsonResponse({'success': False, 'message': f'You need {required_coins} coins to purchase this course. You have {user_profile.coins} coins.'}, status=400)

    try:
        if not user_profile.deduct_coins(required_coins):
            return JsonResponse({'success': False, 'message': 'Failed to deduct coins. Insufficient balance.'}, status=400)
        CourseEnrollment.objects.create(user=request.user, course=course)
        return JsonResponse({
            'success': True,
            'message': 'Course purchased successfully!',
            'new_coins': user_profile.coins,
            'redirect': reverse('courses:course_details', kwargs={'course_id': course.id, 'course_title': slugified_title})
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to purchase course: {str(e)}'}, status=500)

@login_required
def check_enrollment(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Check Enrollment - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:check_enrollment', kwargs={'course_id': course_id, 'course_title': slugified_title}))
    
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    return JsonResponse({'is_enrolled': is_enrolled})

@login_required
def course_details_view(request, course_id, course_title):
    course = get_object_or_404(Course, id=course_id)
    cleaned_title = clean_text(course.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Course Details - Course ID: {course_id}, Original Title: {course.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {course_title}")
    
    if slugified_title != course_title:
        return HttpResponsePermanentRedirect(
            reverse('courses:course_details', kwargs={
                'course_id': course_id,
                'course_title': slugified_title
            })
        )
    
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, 'يجب شراء هذه الدورة لعرض التفاصيل.')
        return redirect('courses:courses')

    videos = course.videos.all()
    for video in videos:
        video.slugified_title = slugify(clean_text(video.title), allow_unicode=True) or 'default-title'
        logger.debug(f"Course Details - Video ID: {video.id}, Original Title: {video.title}, Slugified Title: {video.slugified_title}")
    
    completed_videos_count = VideoProgress.objects.filter(user=request.user, video__course=course, completed=True).count()
    total_videos_count = videos.count()

    context = {
        "course": course,
        "videos": videos,
        "is_enrolled": is_enrolled,
        "completed_videos_count": completed_videos_count,
        "total_videos_count": total_videos_count,
    }
    return render(request, 'courses/course_details.html', context)

@login_required
def watch_video(request, course_id, course_title, video_id, video_title):
    course = get_object_or_404(Course, id=course_id)
    cleaned_course_title = clean_text(course.title)
    slugified_course_title = slugify(cleaned_course_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Watch Video - Course ID: {course_id}, Original Course Title: {course.title}, Cleaned Course Title: {cleaned_course_title}, Slugified Course Title: {slugified_course_title}, Received Course Title: {course_title}")
    
    video = get_object_or_404(Video, id=video_id, course=course)
    cleaned_video_title = clean_text(video.title)
    slugified_video_title = slugify(cleaned_video_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Watch Video - Video ID: {video_id}, Original Video Title: {video.title}, Cleaned Video Title: {cleaned_video_title}, Slugified Video Title: {slugified_video_title}, Received Video Title: {video_title}")
    
    if course_title != slugified_course_title or video_title != slugified_video_title:
        return HttpResponsePermanentRedirect(
            reverse('courses:watch_video', kwargs={
                'course_id': course_id,
                'course_title': slugified_course_title,
                'video_id': video_id,
                'video_title': slugified_video_title
            })
        )
    
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

    if request.method == 'POST' and 'upload_file' in request.POST:
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        if not file:
            messages.error(request, 'يرجى اختيار ملف للرفع.')
            return redirect('courses:watch_video', course_id=course.id, course_title=slugified_course_title, video_id=video.id, video_title=slugified_video_title)

        try:
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
        
        return redirect('courses:watch_video', course_id=course.id, course_title=slugified_course_title, video_id=video.id, video_title=slugified_video_title)

    if request.method == 'POST' and 'submit_task' in request.POST:
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, video=video)
        submitted_answers = request.POST.getlist('answers[]')

        if len(submitted_answers) != len(task.questions):
            messages.error(request, 'يجب الإجابة على جميع الأسئلة.')
            return redirect('courses:watch_video', course_id=course.id, course_title=slugified_course_title, video_id=video.id, video_title=slugified_video_title)

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

        return redirect('courses:watch_video', course_id=course.id, course_title=slugified_course_title, video_id=video.id, video_title=slugified_video_title)

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

        return redirect('courses:watch_video', course_id=course.id, course_title=slugified_course_title, video_id=video.id, video_title=slugified_video_title)

    completed_videos_count = VideoProgress.objects.filter(user=request.user, video__course=course, completed=True).count()
    total_videos_count = videos.count()

    uploaded_files = video.files.all()
    user_rating = VideoRating.objects.filter(video=video, user=request.user).first()
    user_rating = user_rating.rating if user_rating else None

    comments = Comment.objects.filter(video=video).order_by('-created_at')

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
        'comments': comments,
        'slugified_course_title': slugified_course_title,
        'slugified_video_title': slugified_video_title,
    }
    return render(request, 'courses/watch_video.html', context)

@login_required
def rate_video(request, video_id, video_title):
    video = get_object_or_404(Video, id=video_id)
    cleaned_title = clean_text(video.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Rate Video - Video ID: {video_id}, Original Title: {video.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {video_title}")
    
    if slugified_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:rate_video', kwargs={'video_id': video_id, 'video_title': slugified_title}))
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        VideoRating.objects.update_or_create(video=video, user=request.user, defaults={'rating': rating})
        return redirect('courses:watch_video', course_id=video.course.id, course_title=slugify(clean_text(video.course.title), allow_unicode=True) or 'default-title', video_id=video.id, video_title=slugified_title)

@login_required
def add_comment(request, video_id, video_title):
    video = get_object_or_404(Video, id=video_id)
    cleaned_title = clean_text(video.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Comment - Video ID: {video_id}, Original Title: {video.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {video_title}")
    
    if slugified_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_comment', kwargs={'video_id': video_id, 'video_title': slugified_title}))
    
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(video=video, user=request.user, content=content)
        return redirect('courses:watch_video', course_id=video.course.id, course_title=slugify(clean_text(video.course.title), allow_unicode=True) or 'default-title', video_id=video.id, video_title=slugified_title)

@login_required
def update_progress(request, video_id, video_title):
    video = get_object_or_404(Video, id=video_id)
    cleaned_title = clean_text(video.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Update Progress - Video ID: {video_id}, Original Title: {video.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {video_title}")
    
    if slugified_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:update_progress', kwargs={'video_id': video_id, 'video_title': slugified_title}))
    
    if request.method == 'POST':
        current_time = float(request.POST.get('current_time', 0.0))
        video_progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'completed': False, 'progress_percentage': 0.0, 'current_time': 0.0}
        )
        video_progress.current_time = current_time
        duration = video.duration * 60  # Convert minutes to seconds
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

def get_rating(request, video_id, video_title):
    video = get_object_or_404(Video, id=video_id)
    cleaned_title = clean_text(video.title)
    slugified_title = slugify(cleaned_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Get Rating - Video ID: {video_id}, Original Title: {video.title}, Cleaned Title: {cleaned_title}, Slugified Title: {slugified_title}, Received Title: {video_title}")
    
    if slugified_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:get_rating', kwargs={'video_id': video_id, 'video_title': slugified_title}))
    
    if not request.user.is_authenticated:
        return JsonResponse({'rating': None})
    rating = VideoRating.objects.filter(video_id=video_id, user=request.user).first()
    return JsonResponse({'rating': rating.rating if rating else None})

def search_courses(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(title__icontains=query) | Course.objects.filter(description__icontains=query) | Course.objects.filter(category__icontains=query) if query else Course.objects.none()

    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(CourseEnrollment.objects.filter(user=request.user).values_list('course__id', flat=True))

    return render(request, 'courses/search_results.html', {
        'query': query,
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids
    })

@login_required
@instructor_required
def add_task(request, course_id, course_title, video_id, video_title):
    video = get_object_or_404(Video, id=video_id, course__id=course_id, course__instructor=request.user.username)
    cleaned_video_title = clean_text(video.title)
    slugified_video_title = slugify(cleaned_video_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Task - Video ID: {video_id}, Original Video Title: {video.title}, Cleaned Video Title: {cleaned_video_title}, Slugified Video Title: {slugified_video_title}, Received Video Title: {video_title}")
    
    course = video.course
    cleaned_course_title = clean_text(course.title)
    slugified_course_title = slugify(cleaned_course_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Task - Course ID: {course_id}, Original Course Title: {course.title}, Cleaned Course Title: {cleaned_course_title}, Slugified Course Title: {slugified_course_title}, Received Course Title: {course_title}")
    
    if slugified_video_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_task', kwargs={'course_id': course_id, 'course_title': course_title, 'video_id': video_id, 'video_title': slugified_video_title}))
    
    if slugified_course_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_task', kwargs={'course_id': course_id, 'course_title': slugified_course_title, 'video_id': video_id, 'video_title': slugified_video_title}))
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.video = video
            task.questions = form.cleaned_data['questions_json']
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('courses:course_videos', course_id=course_id, course_title=slugified_course_title)
    else:
        form = TaskForm()
    return render(request, 'courses/add_task.html', {'form': form, 'video': video})

@login_required
@instructor_required
def add_alternative_quiz(request, course_id, course_title, video_id, video_title):
    video = get_object_or_404(Video, id=video_id, course__id=course_id, course__instructor=request.user.username)
    cleaned_video_title = clean_text(video.title)
    slugified_video_title = slugify(cleaned_video_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Alternative Quiz - Video ID: {video_id}, Original Video Title: {video.title}, Cleaned Video Title: {cleaned_video_title}, Slugified Video Title: {slugified_video_title}, Received Video Title: {video_title}")
    
    course = video.course
    cleaned_course_title = clean_text(course.title)
    slugified_course_title = slugify(cleaned_course_title, allow_unicode=True) or 'default-title'
    logger.debug(f"Add Alternative Quiz - Course ID: {course_id}, Original Course Title: {course.title}, Cleaned Course Title: {cleaned_course_title}, Slugified Course Title: {slugified_course_title}, Received Course Title: {course_title}")
    
    if slugified_video_title != video_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_alternative_quiz', kwargs={'course_id': course_id, 'course_title': course_title, 'video_id': video_id, 'video_title': slugified_video_title}))
    
    if slugified_course_title != course_title:
        return HttpResponsePermanentRedirect(reverse('courses:add_alternative_quiz', kwargs={'course_id': course_id, 'course_title': slugified_course_title, 'video_id': video_id, 'video_title': slugified_video_title}))
    
    if request.method == 'POST':
        form = AlternativeQuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.video = video
            quiz.save()
            messages.success(request, 'Alternative quiz added successfully!')
            return redirect('courses:course_videos', course_id=course_id, course_title=slugified_course_title)
    else:
        form = AlternativeQuizForm()
    return render(request, 'courses/add_alternative_quiz.html', {'form': form, 'video': video})