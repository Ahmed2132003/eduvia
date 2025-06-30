from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.contrib import messages
from .utils import analyze_user_performance, generate_recommendations, generate_dashboard_report_pdf
from .models import PerformanceReport
from django.contrib.auth import get_user_model
import uuid
from django.utils.timezone import now
from django.http import HttpResponseForbidden

User = get_user_model()

@login_required
def performance_dashboard(request):
    performance_data = analyze_user_performance(request.user)
    recommendations = generate_recommendations(request.user)
    user_reports = PerformanceReport.objects.filter(user=request.user).order_by('-generated_at')
    
    # Prepare data for course completion chart
    course_labels = list(performance_data['course_completion_rates'].keys())
    completion_rates = list(performance_data['course_completion_rates'].values())
    
    context = {
        'performance_data': performance_data,
        'recommendations': recommendations,
        'user_reports': user_reports,
        'course_labels': course_labels,
        'completion_rates': completion_rates,
    }
    return render(request, 'performance_analysis/dashboard.html', context)

@login_required
def download_report(request, report_id):
    try:
        report = PerformanceReport.objects.get(report_id=report_id, user=request.user)
        performance_data = eval(report.performance_summary)
        recommendations = eval(report.recommendations)
        pdf_buffer = generate_dashboard_report_pdf(request.user, performance_data, recommendations)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Performance_Report_{request.user.username}_{now().strftime("%Y%m%d")}.pdf"'
        response.write(pdf_buffer.getvalue())
        return response
    except PerformanceReport.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect('performance_dashboard')


import io
import os
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue, Color
from django.utils import timezone
from performance_analysis.utils import analyze_user_performance
from courses.models import Course
from performance_analysis.models import UserReport

# تحديد ألوان الموقع
PRIMARY_COLOR = Color(0, 0.8, 0.65)  # #00c9a7
SECONDARY_COLOR = darkblue
SKY_BLUE = Color(0.53, 0.81, 0.92)  # #87CEEB

def draw_background(p, width, height, color):
    """إنشاء خلفية بلون موحد."""
    p.setFillColor(color)
    p.rect(0, 0, width, height, fill=1, stroke=0)

@login_required
def request_report_email(request):
    if request.method == 'POST':
        user = request.user
        # تحليل بيانات الأداء
        performance_data = analyze_user_performance(user)
        enrolled_courses = Course.objects.filter(enrollments__user=user)
        course_labels = [course.title for course in enrolled_courses]
        completion_rates = [
            (enrollment.progress / course.total_lessons * 100) if course.total_lessons > 0 else 0
            for course, enrollment in zip(enrolled_courses, user.enrollments.all())
        ]

        # إنشاء تقرير PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # إضافة خلفية سماوي للصفحة الأولى
        draw_background(p, width, height, SKY_BLUE)

        # إضافة الشعارين مع معالجة الأخطاء
        logo_eduvia = os.path.join(settings.MEDIA_ROOT, 'images/logo_eduvia1.jpg')
        logo_creativity = os.path.join(settings.MEDIA_ROOT, 'images/creativity_code.jpg')
        if os.path.exists(logo_eduvia):
            p.drawImage(logo_eduvia, 1 * inch, height - 0.8 * inch, width=1 * inch, height=0.5 * inch)
        else:
            p.setFont("Helvetica", 10)
            p.drawString(1 * inch, height - 0.8 * inch, "Logo Eduvia not found")
        if os.path.exists(logo_creativity):
            p.drawImage(logo_creativity, width - 2 * inch, height - 0.8 * inch, width=1 * inch, height=0.5 * inch)
        else:
            p.setFont("Helvetica", 10)
            p.drawString(width - 2 * inch, height - 0.8 * inch, "Creativity Code logo not found")

        # عنوان التقرير
        p.setFont("Helvetica-Bold", 20)
        p.setFillColor(SECONDARY_COLOR)
        p.drawString(1 * inch, height - 1.2 * inch, "Eduvia Performance Report")
        p.setFont("Helvetica", 12)
        p.setFillColor(black)
        p.drawString(1 * inch, height - 1.5 * inch, f"User: {user.username}")
        p.drawString(1 * inch, height - 1.7 * inch, f"Email: {user.email}")
        p.drawString(1 * inch, height - 1.9 * inch, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}")

        # ملخص الأداء
        y_position = height - 2.5 * inch
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(SECONDARY_COLOR)
        p.drawString(1 * inch, y_position, "Performance Summary")
        p.setFont("Helvetica", 12)
        p.setFillColor(black)
        y_position -= 0.3 * inch
        p.drawString(1.2 * inch, y_position, f"Total Courses Enrolled: {performance_data.get('total_courses', 0)}")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Completed Videos: {performance_data.get('completed_videos', 0)}")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Total Coins: {performance_data.get('total_coins', 0)}")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Average Viewing Time: {performance_data.get('avg_viewing_time', 0):.2f} minutes")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Interaction Rate: {performance_data.get('interaction_rate', 0):.2f}%")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Predicted Completion Rate: {performance_data.get('predicted_completion_rate', 0):.2f}%")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Strength Areas: {', '.join(performance_data.get('strength_areas', []))}")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Weakness Areas: {', '.join(performance_data.get('weakness_areas', []))}")
        y_position -= 0.2 * inch
        p.drawString(1.2 * inch, y_position, f"Competition Performance: {performance_data.get('competition_performance', 0):.2f}%")

        # صفحة جديدة للتحليل النصي
        p.showPage()
        draw_background(p, width, height, SKY_BLUE)

        # تحليل الأداء المفصل
        y_position = height - 1 * inch
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(SECONDARY_COLOR)
        p.drawString(1 * inch, y_position, "Detailed Performance Analysis")
        p.setFont("Helvetica", 12)
        p.setFillColor(black)

        # 1. Total Courses Enrolled
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "1. Total Courses Enrolled")
        y_position -= 0.2 * inch
        total_courses = performance_data.get('total_courses', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {total_courses} course(s)")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This shows the number of courses you are enrolled in. A higher number indicates")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "a broader engagement with our platform. To maximize your learning, consider")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "completing the courses you’ve started before enrolling in new ones.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 2. Completed Videos
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "2. Completed Videos")
        y_position -= 0.2 * inch
        completed_videos = performance_data.get('completed_videos', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {completed_videos} video(s)")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This represents the total number of videos you’ve watched to completion.")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "Completing videos is key to mastering course content. Aim to increase this")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "number by regularly engaging with your enrolled courses.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 3. Total Coins
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "3. Total Coins")
        y_position -= 0.2 * inch
        total_coins = performance_data.get('total_coins', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {total_coins} coin(s)")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "Coins are earned through activities like completing videos or quizzes. They")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "reflect your active participation. Use coins to unlock premium content or")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "continue engaging to earn more.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 4. Average Viewing Time
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "4. Average Viewing Time")
        y_position -= 0.2 * inch
        avg_viewing_time = performance_data.get('avg_viewing_time', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {avg_viewing_time:.2f} minutes")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This is the average time you spend watching videos per session. Longer viewing")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "times suggest deeper engagement. Try to maintain or increase this by setting")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "aside dedicated time for learning.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 5. Interaction Rate
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "5. Interaction Rate")
        y_position -= 0.2 * inch
        interaction_rate = performance_data.get('interaction_rate', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {interaction_rate:.2f}%")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This measures how often you interact with course materials (e.g., quizzes,")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "comments). A higher rate indicates active learning. Boost this by participating")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "in discussions or taking practice tests.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 6. Predicted Completion Rate
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "6. Predicted Completion Rate")
        y_position -= 0.2 * inch
        predicted_completion_rate = performance_data.get('predicted_completion_rate', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {predicted_completion_rate:.2f}%")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This estimates the likelihood of completing your enrolled courses based on")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "your current progress. Improve this by consistently working through lessons.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 7. Strength Areas
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "7. Strength Areas")
        y_position -= 0.2 * inch
        strength_areas = performance_data.get('strength_areas', [])
        p.drawString(1.4 * inch, y_position, f"Value: {', '.join(strength_areas) if strength_areas else 'None'}")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "These are the subjects where you perform well. Leverage these strengths to")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "advance further or mentor others. Consider exploring advanced courses in these")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "areas to deepen your expertise.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # 8. Weakness Areas
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "8. Weakness Areas")
        y_position -= 0.2 * inch
        weakness_areas = performance_data.get('weakness_areas', [])
        p.drawString(1.4 * inch, y_position, f"Value: {', '.join(weakness_areas) if weakness_areas else 'None'}")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "These are areas where you could improve. Focus on these subjects by enrolling")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "in recommended courses or dedicating extra study time to build confidence.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch
        
        # 9. Competition Performance
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "9. Competition Performance")
        y_position -= 0.2 * inch
        competition_performance = performance_data.get('competition_performance', 0)
        p.drawString(1.4 * inch, y_position, f"Value: {competition_performance:.2f}%")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "This compares your performance to other learners. A higher percentage means")
        y_position -= 0.2 * inch
        p.drawString(1.4 * inch, y_position, "you’re outperforming peers. Keep engaging to maintain or improve your ranking.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch
        
        # 10. Course Completion Rates
        y_position -= 0.4 * inch
        p.drawString(1.2 * inch, y_position, "10. Course Completion Rates")
        y_position -= 0.2 * inch
        if course_labels and completion_rates:
            for course_title, rate in zip(course_labels, completion_rates):
                p.drawString(1.4 * inch, y_position, f"{course_title}: {rate:.2f}%")
                y_position -= 0.2 * inch
            p.drawString(1.4 * inch, y_position, "These percentages show how much of each course you’ve completed. Aim to")
            y_position -= 0.2 * inch
            p.drawString(1.4 * inch, y_position, "reach 100% for each course to earn certificates and fully master the content.")
        else:
            p.drawString(1.4 * inch, y_position, "No completion data available.")
            y_position -= 0.2 * inch
            p.drawString(1.4 * inch, y_position, "You haven’t made progress in any courses yet. Start watching videos to track")
            y_position -= 0.2 * inch
            p.drawString(1.4 * inch, y_position, "your completion rates.")
        if y_position < 1 * inch:
            p.showPage()
            draw_background(p, width, height, SKY_BLUE)
            y_position = height - 1 * inch

        # إنهاء الـ PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # حفظ التقرير في قاعدة البيانات
        report_id = str(uuid.uuid4())
        report_file_name = f'reports/performance_report_{user.id}_{report_id}.pdf'
        report_path = os.path.join(settings.MEDIA_ROOT, report_file_name)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'wb') as f:
            f.write(buffer.getvalue())

        UserReport.objects.create(
            user=user,
            report_id=report_id,
            report_file=report_file_name,
            generated_at=timezone.now()
        )

        # إرسال التقرير عبر الإيميل
        email = EmailMessage(
            subject='Your Eduvia Performance Report',
            body='Dear {},\n\nAttached is your performance report.\n\nBest regards,\nEduvia Team'.format(user.username),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach(f'performance_report_{user.id}.pdf', buffer.getvalue(), 'application/pdf')
        email.send()

        messages.success(request, "Report has been sent to your email.")
        return redirect('performance_analysis:dashboard')

    return redirect('performance_analysis:dashboard')