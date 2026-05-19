"""
performance_analysis/views.py
==============================
تم إزالة جميع اعتماديات نظام الاشتراكات والخطط.
الوصول محمي الآن عبر فحص الكورسات الحديثة (آخر 60 يوم).
"""

import io
import os
import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from reportlab.lib.colors import black, darkblue, Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from core.access import can_access_performance_analysis, ACCESS_DENIED_MESSAGE
from courses.models import Course
from performance_analysis.models import PerformanceReport, UserReport
from performance_analysis.utils import (
    analyze_user_performance,
    generate_recommendations,
    generate_dashboard_report_pdf,
)

User = get_user_model()

# ألوان الموقع
PRIMARY_COLOR = Color(0, 0.8, 0.65)
SECONDARY_COLOR = darkblue
SKY_BLUE = Color(0.53, 0.81, 0.92)


def _access_denied_response(request):
    """رد موحَّد عند رفض الوصول."""
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({"detail": ACCESS_DENIED_MESSAGE}, status=403)
    messages.error(request, ACCESS_DENIED_MESSAGE)
    return redirect('/')


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def performance_dashboard(request):
    """لوحة أداء المستخدم - محمية بفحص الكورسات الحديثة."""
    if not can_access_performance_analysis(request.user):
        return _access_denied_response(request)

    performance_data = analyze_user_performance(request.user)
    recommendations = generate_recommendations(request.user)
    user_reports = PerformanceReport.objects.filter(
        user=request.user
    ).order_by('-generated_at')

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


# ---------------------------------------------------------------------------
# Download Report
# ---------------------------------------------------------------------------

@login_required
def download_report(request, report_id):
    """تحميل تقرير PDF - محمي بفحص الكورسات الحديثة."""
    if not can_access_performance_analysis(request.user):
        return _access_denied_response(request)

    try:
        report = PerformanceReport.objects.get(
            report_id=report_id, user=request.user
        )
        performance_data = eval(report.performance_summary)  # noqa: S307
        recommendations = eval(report.recommendations)        # noqa: S307
        pdf_buffer = generate_dashboard_report_pdf(
            request.user, performance_data, recommendations
        )

        response = HttpResponse(content_type='application/pdf')
        filename = (
            f'Performance_Report_{request.user.username}'
            f'_{timezone.now().strftime("%Y%m%d")}.pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf_buffer.getvalue())
        return response

    except PerformanceReport.DoesNotExist:
        messages.error(request, "التقرير غير موجود.")
        return redirect('performance_analysis:dashboard')


# ---------------------------------------------------------------------------
# Request Report via Email
# ---------------------------------------------------------------------------

def _draw_background(p, width, height, color):
    p.setFillColor(color)
    p.rect(0, 0, width, height, fill=1, stroke=0)


@login_required
def request_report_email(request):
    """إرسال تقرير PDF بالبريد الإلكتروني - محمي بفحص الكورسات الحديثة."""
    if not can_access_performance_analysis(request.user):
        return _access_denied_response(request)

    if request.method != 'POST':
        return redirect('performance_analysis:dashboard')

    user = request.user
    performance_data = analyze_user_performance(user)
    enrolled_courses = Course.objects.filter(enrollments__user=user)
    course_labels = [course.title for course in enrolled_courses]
    completion_rates = []
    for course, enrollment in zip(enrolled_courses, user.enrollments.all()):
        if course.total_lessons > 0:
            rate = (enrollment.progress / course.total_lessons * 100)
        else:
            rate = 0
        completion_rates.append(rate)

    # إنشاء PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    _draw_background(p, width, height, SKY_BLUE)

    # شعارات
    logo_eduvia = os.path.join(settings.MEDIA_ROOT, 'images/logo_eduvia1.jpg')
    logo_creativity = os.path.join(settings.MEDIA_ROOT, 'images/creativity_code.jpg')
    if os.path.exists(logo_eduvia):
        p.drawImage(
            logo_eduvia, 1 * inch, height - 0.8 * inch,
            width=1 * inch, height=0.5 * inch
        )
    if os.path.exists(logo_creativity):
        p.drawImage(
            logo_creativity, width - 2 * inch, height - 0.8 * inch,
            width=1 * inch, height=0.5 * inch
        )

    # عنوان التقرير
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(SECONDARY_COLOR)
    p.drawString(1 * inch, height - 1.2 * inch, "Eduvia Performance Report")
    p.setFont("Helvetica", 12)
    p.setFillColor(black)
    p.drawString(1 * inch, height - 1.5 * inch, f"User: {user.username}")
    p.drawString(1 * inch, height - 1.7 * inch, f"Email: {user.email}")
    p.drawString(
        1 * inch, height - 1.9 * inch,
        f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # ملخص الأداء
    y = height - 2.5 * inch
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(SECONDARY_COLOR)
    p.drawString(1 * inch, y, "Performance Summary")
    p.setFont("Helvetica", 12)
    p.setFillColor(black)

    fields = [
        ("Total Courses Enrolled", performance_data.get('total_courses', 0)),
        ("Completed Videos", performance_data.get('completed_videos', 0)),
        ("Total Coins", performance_data.get('total_coins', 0)),
        ("Average Viewing Time", f"{performance_data.get('avg_viewing_time', 0):.2f} minutes"),
        ("Interaction Rate", f"{performance_data.get('interaction_rate', 0):.2f}%"),
        ("Predicted Completion Rate", f"{performance_data.get('predicted_completion_rate', 0):.2f}%"),
        ("Strength Areas", ', '.join(performance_data.get('strength_areas', []))),
        ("Weakness Areas", ', '.join(performance_data.get('weakness_areas', []))),
    ]
    for label, value in fields:
        y -= 0.2 * inch
        if y < 1 * inch:
            p.showPage()
            _draw_background(p, width, height, SKY_BLUE)
            y = height - 1 * inch
        p.drawString(1.2 * inch, y, f"{label}: {value}")

    # معدلات إتمام الكورسات
    y -= 0.4 * inch
    if y < 1 * inch:
        p.showPage()
        _draw_background(p, width, height, SKY_BLUE)
        y = height - 1 * inch
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(SECONDARY_COLOR)
    p.drawString(1 * inch, y, "Course Completion Rates")
    p.setFont("Helvetica", 12)
    p.setFillColor(black)

    if course_labels and completion_rates:
        for title, rate in zip(course_labels, completion_rates):
            y -= 0.2 * inch
            if y < 1 * inch:
                p.showPage()
                _draw_background(p, width, height, SKY_BLUE)
                y = height - 1 * inch
            p.drawString(1.4 * inch, y, f"{title}: {rate:.2f}%")
    else:
        y -= 0.2 * inch
        p.drawString(1.4 * inch, y, "No completion data available.")

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
        generated_at=timezone.now(),
    )

    # إرسال البريد
    email = EmailMessage(
        subject='Your Eduvia Performance Report',
        body=(
            f'Dear {user.username},\n\n'
            'Attached is your performance report.\n\n'
            'Best regards,\nEduvia Team'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach(
        f'performance_report_{user.id}.pdf',
        buffer.getvalue(),
        'application/pdf',
    )
    email.send()

    messages.success(request, "تم إرسال التقرير إلى بريدك الإلكتروني.")
    return redirect('performance_analysis:dashboard')