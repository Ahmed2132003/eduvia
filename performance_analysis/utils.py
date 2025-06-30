from django.db.models import Count, Q, Sum, Avg
from .models import UserPerformance, LearningRecommendation
from courses.models import Course, CourseEnrollment, Video, VideoProgress
from competitions.models import Competition, Participant
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from pathlib import Path
from django.conf import settings
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import PCMYKColor
import re
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging
import numpy as np

# Logger setup
logger = logging.getLogger(__name__)

User = get_user_model()

def clean_text(text):
    """Clean text by removing non-ASCII characters."""
    if not text:
        return ""
    return re.sub(r'[^\x20-\x7E]', ' ', str(text)).strip()

def analyze_user_performance(user):
    """
    Analyze user performance based on course enrollments, video progress, and competition participation.
    Returns a dictionary with performance metrics.
    """
    try:
        profile = user.courses_profile
        performance, created = UserPerformance.objects.get_or_create(user=user)
    except Exception as e:
        logger.error(f"Error fetching profile for user {user.username}: {e}")
        return {
            'total_courses': 0,
            'completed_videos': 0,
            'total_coins': 0,
            'avg_viewing_time': 0.0,
            'interaction_rate': 0.0,
            'strength_areas': [],
            'weakness_areas': [],
            'course_completion_rates': {'No Courses': 0.0},
            'competition_stats': {
                'total_competitions': 0,
                'total_xp': 0,
                'total_coins': 0,
                'overall_rank': 0,
            },
            'predicted_completion_rate': 0.0,
            'total_minutes': 0.0,
            'completed_minutes': 0.0,
        }

    # Course and video metrics
    enrollments = CourseEnrollment.objects.filter(user=user).select_related('course')
    total_courses = enrollments.count()
    
    # Count completed videos
    completed_videos_qs = VideoProgress.objects.filter(user=user, completed=True)
    completed_videos = completed_videos_qs.count()
    
    # Get total coins from profile
    total_coins = profile.coins or 0
    
    # Calculate total and completed minutes
    total_minutes = Video.objects.filter(course__enrollments__user=user).aggregate(
        total_duration=Sum('duration')
    )['total_duration'] or 0.0
    
    completed_minutes = VideoProgress.objects.filter(user=user, completed=True).select_related('video').aggregate(
        total_duration=Sum('video__duration')
    )['total_duration'] or 0.0
    
    # Calculate average viewing time per video
    total_videos = Video.objects.filter(course__enrollments__user=user).count()
    avg_viewing_time = completed_minutes / completed_videos if completed_videos > 0 else total_minutes / total_videos if total_videos > 0 else 0.0
    
    # Calculate interaction rate (percentage of completed videos out of total videos)
    interaction_rate = (completed_videos / total_videos * 100.0) if total_videos > 0 else 0.0

    # Course completion rates
    course_completion_rates = {}
    for enrollment in enrollments:
        course = enrollment.course
        total_videos_in_course = course.videos.count()
        completed_videos_in_course = VideoProgress.objects.filter(
            user=user, video__course=course, completed=True
        ).count()
        completion_rate = (completed_videos_in_course / total_videos_in_course * 100.0) if total_videos_in_course > 0 else 0.0
        course_completion_rates[clean_text(course.title)] = completion_rate
    if not course_completion_rates:
        course_completion_rates = {'No Courses': 0.0}

    # Strength and weakness areas based on category performance
    category_performance = enrollments.values('course__category').annotate(
        total_videos=Count('course__videos', distinct=True)
    )
    strength_areas = []
    weakness_areas = []
    for cat in category_performance:
        category_videos = Video.objects.filter(
            course__enrollments__user=user, course__category=cat['course__category']
        )
        total_videos_in_category = category_videos.count()
        completed_videos_in_category = VideoProgress.objects.filter(
            user=user, video__in=category_videos, completed=True
        ).count()
        completion_rate = (completed_videos_in_category / total_videos_in_category * 100.0) if total_videos_in_category > 0 else 0.0
        category = clean_text(cat['course__category'])
        if completion_rate >= 70.0:
            strength_areas.append(category)
        elif completion_rate < 40.0:
            weakness_areas.append(category)

    # Competition metrics
    participants = Participant.objects.filter(user=user).select_related('competition')
    total_competitions = participants.count()
    total_competition_xp = sum(p.total_xp or 0 for p in participants)
    total_competition_coins = sum(p.total_coins or 0 for p in participants)
    all_participants = Participant.objects.values('user').annotate(
        total_xp=Sum('total_xp')
    ).order_by('-total_xp')
    user_xp = next((p['total_xp'] for p in all_participants if p['user'] == user.id), 0)
    overall_rank = sum(1 for p in all_participants if p['total_xp'] > user_xp) + 1 if user_xp > 0 else 0

    # Predictive model for completion rate
    predicted_completion_rate = 0.0
    completion_rates = list(course_completion_rates.values())
    if completion_rates:
        # Fallback to mean completion rate if insufficient data
        predicted_completion_rate = np.mean(completion_rates)
    
    # Prepare data for logistic regression
    X = []
    y = []
    for enrollment in enrollments:
        total_videos_in_course = enrollment.course.videos.count()
        completed_videos_in_course = VideoProgress.objects.filter(
            user=user, video__course=enrollment.course, completed=True
        ).count()
        if total_videos_in_course > 0:
            completion_rate = completed_videos_in_course / total_videos_in_course * 100.0
            X.append([completion_rate])  # Simplified feature set
            y.append(1 if completion_rate >= 50.0 else 0)

    # Train logistic regression model if sufficient data
    if len(X) >= 5 and len(set(y)) >= 2:  # Require at least 5 samples and two classes
        try:
            X = np.array(X)
            y = np.array(y)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_train_scaled, y_train)
            last_completion_rate = completion_rates[-1] if completion_rates else 0.0
            input_data = scaler.transform([[last_completion_rate]])
            predicted_completion_rate = model.predict_proba(input_data)[0][1] * 100.0
            logger.info(f"LogisticRegression model trained successfully for user {user.username}")
        except Exception as e:
            logger.error(f"Error training model for user {user.username}: {e}")
            predicted_completion_rate = np.mean(completion_rates) if completion_rates else 0.0
    else:
        logger.info(f"Insufficient data for LogisticRegression for user {user.username}. Using mean completion rate: {predicted_completion_rate:.2f}%")

    # Update performance record
    performance.total_courses = total_courses
    performance.completed_videos = completed_videos
    performance.total_coins = total_coins
    performance.avg_viewing_time = avg_viewing_time
    performance.interaction_rate = interaction_rate
    performance.strength_areas = ", ".join(strength_areas)
    performance.weakness_areas = ", ".join(weakness_areas)
    performance.save()

    return {
        'total_courses': total_courses,
        'completed_videos': completed_videos,
        'total_coins': total_coins,
        'avg_viewing_time': avg_viewing_time,
        'interaction_rate': interaction_rate,
        'strength_areas': strength_areas,
        'weakness_areas': weakness_areas,
        'course_completion_rates': course_completion_rates,
        'competition_stats': {
            'total_competitions': total_competitions,
            'total_xp': total_competition_xp,
            'total_coins': total_competition_coins,
            'overall_rank': overall_rank,
        },
        'predicted_completion_rate': predicted_completion_rate,
        'total_minutes': total_minutes,
        'completed_minutes': completed_minutes,
    }

def generate_recommendations(user):
    """
    Generate course recommendations based on user performance.
    Returns a list of LearningRecommendation objects.
    """
    performance = analyze_user_performance(user)
    weakness_areas = performance['weakness_areas']
    strength_areas = performance['strength_areas']
    recommendations = []

    # Recommend courses for weak areas (high priority)
    for category in weakness_areas:
        courses = Course.objects.filter(
            category=category
        ).exclude(
            enrollments__user=user
        ).order_by('difficulty')[:2]
        for course in courses:
            total_videos = course.videos.count()
            avg_viewing_time = performance['avg_viewing_time'] or 5.0
            completion_time_est = total_videos * avg_viewing_time
            progress_factor = performance['interaction_rate'] / 100.0 if performance['interaction_rate'] else 0.5
            recommendation, created = LearningRecommendation.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    'reason': f"Recommended to improve skills in {category}. Estimated completion time: {completion_time_est:.1f} minutes. Progress factor: {progress_factor:.2f}.",
                    'priority': 1,
                }
            )
            recommendations.append(recommendation)

    # Recommend courses for strong areas (lower priority)
    for category in strength_areas:
        courses = Course.objects.filter(
            category=category
        ).exclude(
            enrollments__user=user
        ).order_by('difficulty')[:1]
        for course in courses:
            total_videos = course.videos.count()
            avg_viewing_time = performance['avg_viewing_time'] or 5.0
            completion_time_est = total_videos * avg_viewing_time
            progress_factor = performance['interaction_rate'] / 100.0 if performance['interaction_rate'] else 0.5
            recommendation, created = LearningRecommendation.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    'reason': f"Recommended to advance skills in {category}. Estimated completion time: {completion_time_est:.1f} minutes. Progress factor: {progress_factor:.2f}.",
                    'priority': 2,
                }
            )
            recommendations.append(recommendation)

    return recommendations

def generate_report_pdf(user, performance_data, recommendations):
    """
    Generate a simple PDF performance report.
    Returns a BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=1*inch)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontSize=24, textColor=colors.navy, alignment=1, spaceAfter=20)
    body_style = ParagraphStyle(name='Body', fontSize=12, textColor=colors.black, spaceAfter=10)

    # Title
    elements.append(Paragraph("Performance Report", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # User Info
    full_name = clean_text(user.profile.full_name or user.username)
    elements.append(Paragraph(f"User: {full_name}", body_style))
    elements.append(Paragraph(f"Email: {user.email}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Course Performance
    elements.append(Paragraph("Course Performance Summary", body_style))
    elements.append(Paragraph(f"Total Courses Enrolled: {performance_data['total_courses']}", body_style))
    elements.append(Paragraph(f"Completed Videos: {performance_data['completed_videos']}", body_style))
    elements.append(Paragraph(f"Total Coins: {performance_data['total_coins']}", body_style))
    elements.append(Paragraph(f"Average Viewing Time: {performance_data['avg_viewing_time']:.1f} minutes", body_style))
    elements.append(Paragraph(f"Interaction Rate: {performance_data['interaction_rate']:.1f}%", body_style))
    elements.append(Paragraph(f"Strength Areas: {', '.join(performance_data['strength_areas']) or 'None'}", body_style))
    elements.append(Paragraph(f"Weakness Areas: {', '.join(performance_data['weakness_areas']) or 'None'}", body_style))
    elements.append(Paragraph(f"Predicted Completion Rate: {performance_data['predicted_completion_rate']:.1f}%", body_style))
    elements.append(Paragraph(f"Total Video Minutes: {performance_data['total_minutes']:.1f}", body_style))
    elements.append(Paragraph(f"Completed Video Minutes: {performance_data['completed_minutes']:.1f}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Course Completion Rates
    elements.append(Paragraph("Course Completion Rates", body_style))
    if performance_data['course_completion_rates']:
        for course_title, rate in performance_data['course_completion_rates'].items():
            elements.append(Paragraph(f"{course_title}: {rate:.2f}%", body_style))
    else:
        elements.append(Paragraph("No course completion data available.", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Competition Performance
    comp_stats = performance_data['competition_stats']
    elements.append(Paragraph("Competition Performance", body_style))
    elements.append(Paragraph(f"Total Competitions: {comp_stats['total_competitions']}", body_style))
    elements.append(Paragraph(f"Total XP Earned: {comp_stats['total_xp']}", body_style))
    elements.append(Paragraph(f"Total Coins Earned: {comp_stats['total_coins']}", body_style))
    elements.append(Paragraph(f"Overall Ranking: {comp_stats['overall_rank'] or 'Not ranked'}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Recommendations
    elements.append(Paragraph("Recommended Courses", body_style))
    if recommendations:
        for rec in recommendations:
            elements.append(Paragraph(f"- {rec.course.title}: {rec.reason}", body_style))
    else:
        elements.append(Paragraph("No recommendations available at this time.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_course_completion_chart(course_completion_rates):
    """
    Create a bar chart for course completion rates.
    Returns a Drawing object for the PDF.
    """
    drawing = Drawing(400, 200)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = [list(course_completion_rates.values())] if course_completion_rates else [[0]]
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 20
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.categoryNames = list(course_completion_rates.keys()) if course_completion_rates else ['No Courses']
    bc.bars[0].fillColor = PCMYKColor(0, 80, 80, 0)
    drawing.add(bc)
    return drawing

def create_completed_videos_chart(completed_videos, total_videos):
    """
    Create a pie chart for completed vs. remaining videos.
    Returns a Drawing object for the PDF.
    """
    drawing = Drawing(200, 200)
    pc = Pie()
    pc.x = 65
    pc.y = 15
    pc.width = 120
    pc.height = 120
    pc.data = [completed_videos, max(total_videos - completed_videos, 0)] if total_videos > 0 else [0, 1]
    pc.labels = ['Completed Videos', 'Remaining Videos'] if total_videos > 0 else ['No Videos', '']
    pc.slices.strokeColor = colors.black
    pc.slices[0].fillColor = PCMYKColor(0, 80, 80, 0)
    pc.slices[1].fillColor = PCMYKColor(20, 20, 20, 10)
    drawing.add(pc)
    return drawing

def generate_dashboard_report_pdf(user, performance_data, recommendations):
    """
    Generate a detailed PDF performance dashboard report with charts.
    Returns a BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=1*inch)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontSize=24, textColor=colors.navy, alignment=1, spaceAfter=20)
    subtitle_style = ParagraphStyle(name='Subtitle', fontSize=16, textColor=colors.black, spaceAfter=15)
    body_style = ParagraphStyle(name='Body', fontSize=12, textColor=colors.black, spaceAfter=10)

    # Logos
    eduvia_logo_path = Path(settings.STATIC_ROOT) / 'images' / 'logo_eduvia1.png'
    company_logo_path = Path(settings.STATIC_ROOT) / 'images' / 'creativity_code.png'
    if eduvia_logo_path.exists():
        elements.append(Image(str(eduvia_logo_path), width=2*inch, height=0.5*inch))
    if company_logo_path.exists():
        elements.append(Image(str(company_logo_path), width=2*inch, height=0.5*inch))
    elements.append(Spacer(1, 0.2*inch))

    # Title
    elements.append(Paragraph("Eduvia Performance Dashboard Report", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # User Info
    full_name = clean_text(user.profile.full_name or user.username)
    elements.append(Paragraph(f"User: {full_name}", body_style))
    elements.append(Paragraph(f"Email: {user.email}", body_style))
    elements.append(Paragraph(f"Generated on: {now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Course Performance
    elements.append(Paragraph("Course Performance Summary", subtitle_style))
    elements.append(Paragraph(f"Total Courses Enrolled: {performance_data['total_courses']}", body_style))
    elements.append(Paragraph(f"Completed Videos: {performance_data['completed_videos']}", body_style))
    elements.append(Paragraph(f"Total Coins: {performance_data['total_coins']}", body_style))
    elements.append(Paragraph(f"Average Viewing Time: {performance_data['avg_viewing_time']:.1f} minutes", body_style))
    elements.append(Paragraph(f"Interaction Rate: {performance_data['interaction_rate']:.1f}%", body_style))
    elements.append(Paragraph(f"Predicted Completion Rate: {performance_data['predicted_completion_rate']:.1f}%", body_style))
    elements.append(Paragraph(f"Total Video Minutes: {performance_data['total_minutes']:.1f}", body_style))
    elements.append(Paragraph(f"Completed Video Minutes: {performance_data['completed_minutes']:.1f}", body_style))
    elements.append(Paragraph(f"Strength Areas: {', '.join(performance_data['strength_areas']) or 'None'}", body_style))
    elements.append(Paragraph(f"Weakness Areas: {', '.join(performance_data['weakness_areas']) or 'None'}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Course Completion Rates Chart
    elements.append(Paragraph("Course Completion Rates", subtitle_style))
    if performance_data['course_completion_rates'] and any(v > 0 for v in performance_data['course_completion_rates'].values()):
        elements.append(create_course_completion_chart(performance_data['course_completion_rates']))
    else:
        elements.append(Paragraph("No course completion data available to display chart.", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Completed Videos Chart
    total_videos = performance_data['completed_videos'] + (
        performance_data['total_minutes'] / (performance_data['avg_viewing_time'] or 5.0)
        if performance_data['avg_viewing_time'] else 0
    )
    elements.append(Paragraph("Completed Videos", subtitle_style))
    if total_videos > 0:
        elements.append(create_completed_videos_chart(performance_data['completed_videos'], total_videos))
    else:
        elements.append(Paragraph("No video data available to display chart.", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Competition Performance
    comp_stats = performance_data['competition_stats']
    elements.append(Paragraph("Competition Performance", subtitle_style))
    elements.append(Paragraph(f"Total Competitions: {comp_stats['total_competitions']}", body_style))
    elements.append(Paragraph(f"Total XP Earned: {comp_stats['total_xp']}", body_style))
    elements.append(Paragraph(f"Total Coins Earned: {comp_stats['total_coins']}", body_style))
    elements.append(Paragraph(f"Overall Ranking: {comp_stats['overall_rank'] or 'Not ranked'}", body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Recommendations
    elements.append(Paragraph("Recommended Courses", subtitle_style))
    if recommendations:
        for rec in recommendations:
            elements.append(Paragraph(f"- {rec.course.title}: {rec.reason}", body_style))
    else:
        elements.append(Paragraph("No recommendations available at this time.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer