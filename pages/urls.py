from django.urls import path
from .views import home_view,about_us_view,contact_us_view

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_us_view, name='about'),
    path('contact_us/',contact_us_view,name='contact_us',)
]
