from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'performance_analysis'

urlpatterns = [
    path('dashboard/', views.performance_dashboard, name='dashboard'),
    path('download/<str:report_id>/', views.download_report, name='download_report'),
    path('request-report-email/', views.request_report_email, name='request_report_email'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

