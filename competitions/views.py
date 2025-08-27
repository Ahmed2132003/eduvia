from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponsePermanentRedirect
from django.utils import timezone
from django.utils.text import slugify
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import os
from django.conf import settings
import logging
import uuid
import re
from .models import Competition, Participant, Question, Answer, Certificate
from .forms import CompetitionForm
from django.urls import reverse
from accounts.models import Profile  # أضف هذا الاستيراد

logger = logging.getLogger(__name__)

def clean_text(text):
    """تنظيف النص من الأحرف غير المدعومة مع دعم الأحرف العربية"""
    if not text or not text.strip():
        return 'default-title'
    text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', str(text)).strip()
    cleaned = text if text else 'default-title'
    slugified = slugify(cleaned, allow_unicode=True)
    return slugified if slugified else 'default-title'

def check_instructor(user):
    return user.is_authenticated and user.role == 'instructor'

def check_student(user):
    return user.is_authenticated and user.role == 'student'

def redirect_old_competition_url(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)
    return HttpResponsePermanentRedirect(
        reverse('competitions:competition_detail', kwargs={
            'competition_id': competition.id,
            'competition_title': cleaned_title
        })
    )

@login_required
def competition_list(request):
    competitions = Competition.objects.all()
    now = timezone.now()
    profile = Profile.objects.get(user=request.user)  # أضف هذا
    logger.info(f"Rendering competition_list: now={now}, user={request.user.username}, competitions_count={competitions.count()}")
    for competition in competitions:
        logger.info(f"Competition '{competition.title}': start_time={competition.start_time}, end_time={competition.end_time}, is_active={competition.is_active}, is_ongoing={competition.is_ongoing}")
    return render(request, 'competitions/competition_list.html', {
        'competitions': competitions,
        'now': now,
        'subscription_plan': profile.subscription_plan  # أضف هذا للـ context
    })

@login_required
def create_competition(request):
    if not check_instructor(request.user):
        raise PermissionDenied("Only instructors can create competitions.")
    
    profile = get_object_or_404(Profile, user=request.user)
    now = timezone.now()
    if profile.subscription_plan != 'instructor' or (profile.subscription_end_date and profile.subscription_end_date < now):
        messages.error(request, "يجب أن تكون مشتركًا في خطة المحاضرين لإنشاء مسابقات. اشترك الآن.")
        return redirect('accounts:subscribe')
    
    # عدد المسابقات الموجودة
    current_comps = Competition.objects.filter(instructor=request.user).count()
    max_comps = 0
    duration = profile.subscription_duration
    if duration == 'monthly':
        max_comps = 2
    elif duration == 'six_months':
        max_comps = 4
    elif duration == 'yearly':
        max_comps = float('inf')
    
    if current_comps >= max_comps:
        messages.error(request, f"لقد تجاوزت الحد الأقصى لإنشاء المسابقات في خطتك ({duration}). اشترك في مدة أطول أو خطة أعلى.")
        return redirect('accounts:subscribe')
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.instructor = request.user
            cleaned_title = clean_text(competition.title)
            if not cleaned_title:
                messages.error(request, "العنوان غير صالح. يرجى إدخال عنوان يحتوي على أحرف صالحة.")
                return render(request, 'competitions/create_competition.html', {'form': form})
            competition.save()
            logger.info(f"Competition created: {competition}")
            messages.success(request, "Competition created successfully!")
            return redirect('competitions:competition_detail', competition_id=competition.id, competition_title=cleaned_title)
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, form.errors)
    else:
        form = CompetitionForm()
    
    return render(request, 'competitions/create_competition.html', {'form': form})

@login_required
def competition_detail(request, competition_id, competition_title):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)
    logger.debug(f"Competition Detail - ID: {competition_id}, Original Title: {competition.title}, Cleaned Title: {cleaned_title}, Received Title: {competition_title}")
    
    if cleaned_title != competition_title:
        return HttpResponsePermanentRedirect(
            reverse('competitions:competition_detail', kwargs={
                'competition_id': competition_id,
                'competition_title': cleaned_title
            })
        )
    
    is_participant = False
    participant = None
    questions_with_status = []
    profile = Profile.objects.get(user=request.user)  # أضف هذا

    if check_student(request.user):
        is_participant = Participant.objects.filter(
            user=request.user, competition=competition
        ).exists()
        participant = Participant.objects.filter(user=request.user, competition=competition).first()
        
        if participant:
            for question in competition.questions.all():
                answered = participant.answers.filter(question=question).exists()
                questions_with_status.append({
                    'question': question,
                    'answered': answered
                })

    return render(request, 'competitions/competition_detail.html', {
        'competition': competition,
        'is_participant': is_participant,
        'participant': participant,
        'is_instructor': check_instructor(request.user),
        'questions_with_status': questions_with_status,
        'slugified_competition_title': cleaned_title,
        'subscription_plan': profile.subscription_plan  # أضف هذا
    })

@login_required
def edit_competition(request, competition_id, competition_title):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)

    if cleaned_title != competition_title:
        return redirect('competitions:edit_competition', competition_id=competition_id, competition_title=cleaned_title)

    profile = get_object_or_404(Profile, user=request.user)
    if not check_instructor(request.user):
        messages.error(request, "Only instructors can edit competitions.")
        return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)

    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            messages.success(request, "Competition updated successfully!")
            return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompetitionForm(instance=competition)

    return render(request, 'competitions/edit_competition.html', {
        'form': form,
        'competition': competition,
    })

@login_required
def join_competition(request, competition_id, competition_title):
    if not check_student(request.user):
        raise PermissionDenied("Only students can join competitions.")
    
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)
    logger.debug(f"Join Competition - ID: {competition_id}, Original Title: {competition.title}, Cleaned Title: {cleaned_title}, Received Title: {competition_title}")
    
    if cleaned_title != competition_title:
        return HttpResponsePermanentRedirect(
            reverse('competitions:join_competition', kwargs={
                'competition_id': competition_id,
                'competition_title': cleaned_title
            })
        )
    
    now = timezone.now()
    if not competition.is_active or competition.end_time < now:
        messages.error(request, "This competition is not available for joining.")
        return redirect('competitions:competition_detail', competition_id=competition.id, competition_title=cleaned_title)
    
    profile = get_object_or_404(Profile, user=request.user)
    plan = profile.subscription_plan or 'free'
    
    # تعديل اللوجيك: لو 'free'، استمر بدون تحقق end_date، بس لو خطة أخرى وexpired، منع
    if plan != 'free' and (not profile.subscription_end_date or profile.subscription_end_date < now):
        messages.error(request, "خطتك المدفوعة منتهية الصلاحية. اشترك مرة أخرى للانضمام إلى المسابقات.")
        return redirect('accounts:subscribe')
    
    # عدد الاشتراكات
    current_joins = Participant.objects.filter(user=request.user).count()
    month_joins = Participant.objects.filter(user=request.user, joined_at__month=now.month, joined_at__year=now.year).count()
    
    max_joins = 0
    if plan == 'free':
        max_joins = 1  # إجمالي
    elif plan == 'basic':
        max_joins = 2
        current_joins = month_joins
    elif plan == 'pro':
        max_joins = 4
    elif plan == 'premium':
        max_joins = float('inf')
    
    if current_joins >= max_joins:
        messages.error(request, f"لقد تجاوزت الحد الأقصى للانضمام في خطتك ({plan}). اشترك في خطة أعلى للمزيد.")
        return redirect('accounts:subscribe')
    
    Participant.objects.get_or_create(user=request.user, competition=competition)
    messages.success(request, "You have joined the competition!")
    return redirect('competitions:competition_detail', competition_id=competition.id, competition_title=cleaned_title)

@login_required
def add_question(request, competition_id, competition_title):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)

    if cleaned_title != competition_title:
        return redirect('competitions:add_question', competition_id=competition_id, competition_title=cleaned_title)

    profile = get_object_or_404(Profile, user=request.user)
    if not check_instructor(request.user):
        messages.error(request, "Only instructors can add questions.")
        return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)

    if request.method == 'POST':
        text = request.POST.get('text')
        question_type = request.POST.get('question_type')
        choices = request.POST.get('choices', '')
        correct_answer = request.POST.get('correct_answer')
        points = request.POST.get('points')
        coins = request.POST.get('coins')

        if text and question_type and correct_answer and points and coins:
            try:
                points = int(points)
                coins = int(coins)
                if points < 0 or coins < 0:
                    messages.error(request, "Points and coins must be non-negative.")
                else:
                    question = Question(
                        competition=competition,
                        text=text,
                        question_type=question_type,
                        choices=choices,
                        correct_answer=correct_answer,
                        points=points,
                        coins=coins
                    )
                    question.save()
                    messages.success(request, "Question added successfully!")
                    return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)
            except ValueError:
                messages.error(request, "Invalid points or coins value.")
        else:
            messages.error(request, "All required fields must be filled.")

    return render(request, 'competitions/add_question.html', {
        'competition': competition,
    })

@login_required
def answer_question(request, competition_id, competition_title, question_id):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)

    if cleaned_title != competition_title:
        return redirect('competitions:answer_question', competition_id=competition_id, competition_title=cleaned_title, question_id=question_id)

    if not check_student(request.user):
        messages.error(request, "Only students can answer questions.")
        return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)

    participant = get_object_or_404(Participant, user=request.user, competition=competition)

    if not competition.is_ongoing:
        messages.error(request, "This competition is not active.")
        return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)

    question = get_object_or_404(Question, id=question_id, competition=competition)

    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        try:
            Answer.objects.create(
                participant=participant,
                question=question,
                answer_text=answer_text
            )
            is_correct = False
            if question.question_type == 'MCQ':
                correct_answer = question.correct_answer
                is_correct = answer_text == correct_answer
            else:
                correct_answer = question.correct_answer.lower().strip()
                is_correct = answer_text.lower().strip() == correct_answer

            if is_correct and request.user.courses_profile:
                request.user.courses_profile.xp += question.points
                request.user.courses_profile.coins += question.points // 10
                request.user.courses_profile.save()

            messages.success(request, "Answer submitted! {}".format("Correct!" if is_correct else "Incorrect."))
        except:
            messages.error(request, "You have already answered this question.")

        return redirect('competitions:competition_detail', competition_id=competition_id, competition_title=cleaned_title)

    choices = question.choices.split(',') if question.question_type == 'MCQ' and question.choices else []

    return render(request, 'competitions/answer_question.html', {
        'competition': competition,
        'question': question,
        'choices': choices,
    })

@login_required
def download_certificate(request, competition_id, competition_title):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)
    logger.debug(f"Download Certificate - ID: {competition_id}, Original Title: {competition.title}, Cleaned Title: {cleaned_title}, Received Title: {competition_title}")
    
    if cleaned_title != competition_title:
        return HttpResponsePermanentRedirect(
            reverse('competitions:download_certificate', kwargs={
                'competition_id': competition_id,
                'competition_title': cleaned_title
            })
        )
    
    participant = get_object_or_404(Participant, user=request.user, competition=competition)
    
    profile = get_object_or_404(Profile, user=request.user)
    plan = profile.subscription_plan or 'free'
    participants = Participant.objects.filter(competition=competition).order_by('-total_xp')
    rank = list(participants).index(participant) + 1
    
    if rank <= 3 and plan == 'free':
        messages.error(request, "في الخطة المجانية، لا يمكنك الحصول على شهادة إذا كنت من الأوائل 3. اشترك في خطة مدفوعة.")
        return redirect('accounts:subscribe')
    
    if not participant.has_completed_competition():
        messages.error(request, "You must complete all questions to download the certificate.")
        return redirect('competitions:competition_detail', competition_id=competition.id, competition_title=cleaned_title)
    
    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        competition=competition,
        defaults={'certificate_number': str(uuid.uuid4())}
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=1*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontName='Times-Roman', fontSize=32, textColor=colors.navy, alignment=1, spaceAfter=20, leading=36)
    subtitle_style = ParagraphStyle(name='Subtitle', fontName='Times-Roman', fontSize=20, textColor=colors.white, alignment=1, spaceAfter=15, leading=24)
    body_style = ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=16, textColor=colors.white, alignment=1, spaceAfter=12, leading=20)
    stamp_style = ParagraphStyle(name='Stamp', fontName='Times-Roman', fontSize=14, textColor=colors.navy, alignment=1, spaceAfter=8, leading=16)
    signature_style = ParagraphStyle(name='Signature', fontName='Times-Italic', fontSize=12, textColor=colors.navy, alignment=1, spaceAfter=12, leading=14)
    
    competition_title_cleaned = clean_text(competition.title)
    try:
        full_name = clean_text(request.user.courses_profile.full_name or request.user.username)
    except AttributeError:
        full_name = clean_text(request.user.username)
    instructor = clean_text(competition.instructor.username)
    
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
    elements.append(Paragraph(f"This certificate is proudly presented to <b>{full_name}</b> for successfully completing the competition", body_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>{competition_title_cleaned}</b>", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Instructed by: {instructor}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Congratulations on your dedication and achievement!", body_style))
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
    response['Content-Disposition'] = f'attachment; filename="certificate_{competition_title_cleaned}_{request.user.username}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response

@login_required
def leaderboard(request, competition_id, competition_title):
    competition = get_object_or_404(Competition, id=competition_id)
    cleaned_title = clean_text(competition.title)
    
    if cleaned_title != competition_title:
        return HttpResponsePermanentRedirect(
            reverse('competitions:leaderboard', kwargs={
                'competition_id': competition_id,
                'competition_title': cleaned_title
            })
        )
    
    participants = Participant.objects.filter(competition=competition).order_by('-total_xp')
    
    return render(request, 'competitions/leaderboard.html', {
        'competition': competition,
        'participants': participants,
        'slugified_competition_title': cleaned_title,
    })