from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .utils import analyze_user_performance, generate_recommendations, generate_dashboard_report_pdf
from .models import PerformanceReport
import uuid
from django.utils.timezone import now
import logging

# إعداد Logger
logger = logging.getLogger(__name__)

def send_dashboard_report(user_id):
    try:
        logger.info(f"Starting report generation for user_id: {user_id}")
        User = get_user_model()
        user = User.objects.get(id=user_id)
        logger.info(f"User found: {user.username}, email: {user.email}")
        
        performance_data = analyze_user_performance(user)
        logger.info(f"Performance data generated for {user.username}: {performance_data}")
        
        recommendations = generate_recommendations(user)
        logger.info(f"Recommendations generated for {user.username}: {len(recommendations)} recommendations")
        
        pdf_buffer = generate_dashboard_report_pdf(user, performance_data, recommendations)
        logger.info(f"PDF generated for {user.username}")
        
        report = PerformanceReport.objects.create(
            user=user,
            report_id=str(uuid.uuid4()),
            performance_summary=str(performance_data),
            recommendations=str([f"{rec.course.title}: {rec.reason}" for rec in recommendations]),
            emailed=True
        )
        logger.info(f"Performance report created for {user.username}, report_id: {report.report_id}")
        
        email = EmailMessage(
            subject='Your Eduvia Performance Dashboard Report',
            body='Please find attached your performance dashboard report.',
            from_email='creativitycode78@gmail.com',
            to=[user.email],
        )
        email.attach(f'Performance_Report_{user.username}_{now().strftime("%Y%m%d")}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send()
        logger.info(f"Email sent successfully to {user.email}")
        
        return f"Report sent to {user.email}"
    except Exception as e:
        logger.error(f"Error sending report to user {user_id}: {str(e)}", exc_info=True)
        return f"Error sending report to user {user_id}: {str(e)}"

def send_dashboard_report_to_all():
    try:
        logger.info("Starting send_dashboard_report_to_all task")
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        logger.info(f"Found {users.count()} active users")
        for user in users:
            logger.info(f"Sending report for user: {user.username}")
            result = send_dashboard_report(user.id)  # تنفيذ مباشر بدون .delay
            logger.info(result)
        logger.info("All reports sent successfully")
        return "Reports sent to all active users"
    except Exception as e:
        logger.error(f"Error in send_dashboard_report_to_all: {str(e)}", exc_info=True)
        return f"Error in send_dashboard_report_to_all: {str(e)}"