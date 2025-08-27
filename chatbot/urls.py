from django.urls import path
from .views import chatbot_page
app_name = 'chatbot'  

urlpatterns = [
    path('', chatbot_page, name='chatbot_page'),  
    path('<int:chat_id>/', chatbot_page, name='chatbot_page_with_id'),
]