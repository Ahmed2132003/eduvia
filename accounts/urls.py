from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.user_chat, name='user_chat'),
    path('messages/', views.user_messages, name='user_messages'),
    path('verify/', views.verify_code_view, name='verify_code'),
    path('verify-form/', views.verify_code_form_view, name='verify_code_form'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)