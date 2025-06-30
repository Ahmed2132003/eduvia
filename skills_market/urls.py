from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'skills_market'

urlpatterns = [
    path('skills/', views.skills_list, name='skills_list'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('services/', views.services_list, name='services_list'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/order/<int:service_id>/', views.order_service, name='order_service'),
    path('opportunities/', views.opportunities_list, name='opportunities_list'),
    path('opportunities/add/', views.add_opportunity, name='add_opportunity'),
    path('opportunities/apply/<int:opportunity_id>/', views.apply_opportunity, name='apply_opportunity'),
    path('opportunities/applications/', views.opportunity_applications, name='opportunity_applications'),
    path('opportunities/applications/accept/<int:application_id>/', views.accept_application, name='accept_application'),
    path('applicant/messages/', views.applicant_messages, name='applicant_messages'),  
    path('applicant/messages/chat/<int:order_id>/', views.applicant_chat, name='applicant_chat'),  
    path('track_service/<int:order_id>/', views.track_service, name='track_service'),
    path('messages/', views.provider_messages, name='provider_messages'),
    path('opportunities/applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('messages/chat/<int:order_id>/', views.provider_chat, name='provider_chat'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)