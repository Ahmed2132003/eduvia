from django.urls import path
from .views import chatbot_page

urlpatterns = [
    path('', chatbot_page, name='chatbot_page'),  # هذا هو المسار الرئيسي لصفحة الشات بوت
]