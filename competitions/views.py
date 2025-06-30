from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Competition, Question, Participant, Answer, Certificate
from .forms import CompetitionForm
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

logger = logging.getLogger(__name__)

def check_instructor(user):
    return user.is_authenticated and user.role == 'instructor'

def check_student(user):
    return user.is_authenticated and user.role == 'student'

@login_required
def competition_list(request):
    competitions = Competition.objects.all()
    now = timezone.now()
    logger.info(f"Rendering competition_list: now={now}, user={request.user.username}, competitions_count={competitions.count()}")
    for competition in competitions:
        logger.info(f"Competition '{competition.title}': start_time={competition.start_time}, end_time={competition.end_time}, is_active={competition.is_active}, is_ongoing={competition.is_ongoing}")
    return render(request, 'competitions/competition_list.html', {
        'competitions': competitions,
        'now': now
    })

@login_required
def create_competition(request):
    if not check_instructor(request.user):
        raise PermissionDenied("Only instructors can create competitions.")
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.instructor = request.user
            competition.save()
            logger.info(f"Competition created: {competition}")
            messages.success(request, "Competition created successfully!")
            return redirect('competition_detail', competition_id=competition.id)
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, form.errors)
    else:
        form = CompetitionForm()
    
    return render(request, 'competitions/create_competition.html', {'form': form})

@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    is_participant = False
    participant = None
    questions_with_status = []

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
    })

@login_required
def edit_competition(request, competition_id):
    if not check_instructor(request.user):
        raise PermissionDenied("Only instructors can edit competitions.")
    
    competition = get_object_or_404(Competition, id=competition_id)
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            competition = form.save()
            messages.success(request, "Competition updated successfully!")
            return redirect('competition_detail', competition_id=competition.id)
        else:
            messages.error(request, form.errors)
    else:
        form = CompetitionForm(instance=competition)
    
    return render(request, 'competitions/edit_competition.html', {'form': form, 'competition': competition})

@login_required
def join_competition(request, competition_id):
    if not check_student(request.user):
        raise PermissionDenied("Only students can join competitions.")
    
    competition = get_object_or_404(Competition, id=competition_id)
    now = timezone.now()
    if not competition.is_active or competition.end_time < now:
        messages.error(request, "This competition is not available for joining.")
        return redirect('competition_detail', competition_id=competition.id)
    
    Participant.objects.get_or_create(user=request.user, competition=competition)
    messages.success(request, "You have joined the competition!")
    return redirect('competition_detail', competition_id=competition.id)

@login_required
def add_question(request, competition_id):
    if not check_instructor(request.user):
        raise PermissionDenied("Only instructors can add questions.")
    
    competition = get_object_or_404(Competition, id=competition_id)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        question_type = request.POST.get('question_type')
        choices = request.POST.get('choices')
        correct_answer = request.POST.get('correct_answer')
        points = request.POST.get('points')
        coins = request.POST.get('coins')
        
        try:
            Question.objects.create(
                competition=competition,
                text=text,
                question_type=question_type,
                choices=choices,
                correct_answer=correct_answer,
                points=int(points) if points else 0,
                coins=int(coins) if coins else 0
            )
            messages.success(request, "Question added successfully!")
            return redirect('competition_detail', competition_id=competition.id)
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
    
    return render(request, 'competitions/add_question.html', {'competition': competition})

@login_required
def answer_question(request, competition_id, question_id):
    if not check_student(request.user):
        raise PermissionDenied("Only students can answer questions.")
    
    competition = get_object_or_404(Competition, id=competition_id)
    question = get_object_or_404(Question, id=question_id, competition=competition)
    participant = get_object_or_404(Participant, user=request.user, competition=competition)
    
    if not competition.is_ongoing:
        messages.error(request, "This competition is not active.")
        return redirect('competition_detail', competition_id=competition.id)
    
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        try:
            Answer.objects.create(
                participant=participant,
                question=question,
                answer_text=answer_text
            )
            messages.success(request, "Answer submitted!")
        except:
            messages.error(request, "You have already answered this question.")
        
        return redirect('competition_detail', competition_id=competition.id)
    
    choices = question.choices.split(',') if question.question_type == 'MCQ' and question.choices else []
    
    return render(request, 'competitions/answer_question.html', {
        'competition': competition,
        'question': question,
        'choices': choices,
    })

@login_required
def leaderboard(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    participants = Participant.objects.filter(competition=competition).order_by('-total_xp')
    return render(request, 'competitions/leaderboard.html', {
        'competition': competition,
        'participants': participants,
    })

@login_required
def download_competition_certificate(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    participant = get_object_or_404(Participant, user=request.user, competition=competition)

    # Check if competition has ended
    now = timezone.now()
    if competition.is_active or competition.end_time > now:
        messages.error(request, 'The competition is still ongoing. Certificates are available after the competition ends.')
        return redirect('competition_detail', competition_id=competition.id)

    # Determine participant's rank
    participants = Participant.objects.filter(competition=competition).order_by('-total_xp')
    participant_ranks = {p.id: idx + 1 for idx, p in enumerate(participants)}
    participant_rank = participant_ranks.get(participant.id, None)

    # Check if participant is in top 3
    if participant_rank is None or participant_rank > 3:
        messages.error(request, 'Certificates are only available for the top 3 participants.')
        return redirect('competition_detail', competition_id=competition.id)

    # Create or retrieve certificate
    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        competition=competition,
        defaults={'certificate_number': str(uuid.uuid4())}
    )

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=1*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    # Set up styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        fontName='Times-Roman',
        fontSize=32,
        textColor=colors.navy,
        alignment=1,
        spaceAfter=20,
        leading=36
    )
    subtitle_style = ParagraphStyle(
        name='Subtitle',
        fontName='Times-Roman',
        fontSize=20,
        textColor=colors.white,
        alignment=1,
        spaceAfter=15,
        leading=24
    )
    body_style = ParagraphStyle(
        name='Body',
        fontName='Times-Roman',
        fontSize=16,
        textColor=colors.white,
        alignment=1,
        spaceAfter=12,
        leading=20
    )
    stamp_style = ParagraphStyle(
        name='Stamp',
        fontName='Times-Roman',
        fontSize=14,
        textColor=colors.navy,
        alignment=1,
        spaceAfter=8,
        leading=16
    )
    signature_style = ParagraphStyle(
        name='Signature',
        fontName='Times-Italic',
        fontSize=12,
        textColor=colors.navy,
        alignment=1,
        spaceAfter=12,
        leading=14
    )

    # Clean text function
    def clean_text(text):
        if not text:
            return ""
        return ''.join(c for c in str(text) if c.isprintable())

    # Prepare text
    competition_title = clean_text(competition.title)
    try:
        full_name = clean_text(request.user.profile.full_name or request.user.username)
    except AttributeError:
        logger.warning(f"Profile not found for user: {request.user.username}")
        full_name = clean_text(request.user.username)
    instructor = clean_text(competition.instructor.username)
    rank_text = {1: "1st", 2: "2nd", 3: "3rd"}.get(participant_rank, f"{participant_rank}th")

    # Add logos
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo_eduvia1.png')
    company_logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'creativity_code.png')
    logo_table_data = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([logo])
    else:
        logger.error(f"Eduvia logo not found at {logo_path}")
        logo_table_data.append([Paragraph("Eduvia Logo", body_style)])
    if os.path.exists(company_logo_path):
        company_logo = Image(company_logo_path, width=1.5*inch, height=1.5*inch)
        logo_table_data.append([company_logo])
    else:
        logger.error(f"Company logo not found at {company_logo_path}")
        logo_table_data.append([Paragraph("Creativity Code Logo", body_style)])

    logo_table = Table([[logo_table_data[0][0], '', logo_table_data[1][0]]], colWidths=[2*inch, 4*inch, 2*inch])
    logo_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (-1,-1), (-1,-1), 'RIGHT'),
    ]))
    elements.append(logo_table)
    elements.append(Spacer(1, 0.3*inch))

    # Certificate title
    elements.append(Paragraph("Certificate of Achievement", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Platform name
    elements.append(Paragraph("Eduvia", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    # Congratulatory message
    elements.append(Paragraph(
        f"This certificate is proudly presented to <b>{full_name}</b> for achieving",
        body_style
    ))
    elements.append(Paragraph(
        f"<b>{rank_text} Place</b> in the competition",
        subtitle_style
    ))
    elements.append(Paragraph(
        f"<b>{competition_title}</b>",
        subtitle_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    # XP earned
    elements.append(Paragraph(
        f"Total XP Earned: {participant.total_xp}",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    # Instructor
    elements.append(Paragraph(
        f"Instructed by: {instructor}",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    # Additional message
    elements.append(Paragraph(
        "Congratulations on your outstanding performance! Keep competing and excelling!",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    # Certificate number and issue date
    elements.append(Paragraph(
        f"Certificate Number: {certificate.certificate_number}",
        body_style
    ))
    elements.append(Paragraph(
        f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}",
        body_style
    ))
    elements.append(Spacer(1, 0.5*inch))

    # Stamp and signature
    elements.append(Paragraph("Certified by: Eduvia", stamp_style))
    elements.append(Paragraph("Eng. Ahmed Ibrahim", signature_style))

    # Draw border and background
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
        canvas.restoreState()

    # Build PDF
    doc.build(elements, onFirstPage=draw_border_and_background, onLaterPages=draw_border_and_background)
    buffer.seek(0)

    # Return PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{competition_title}_{request.user.username}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response