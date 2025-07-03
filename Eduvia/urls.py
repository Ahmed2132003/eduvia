from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('courses/', include('courses.urls')),
    path("chatbot/", include("chatbot.urls")),
    path("competitions/", include("competitions.urls")),
    path('performance/', include('performance_analysis.urls')),
    path('projects/', include('projects.urls')),
    path('skills_market/', include('skills_market.urls')),
    path("mentorship/", include("mentorship.urls")),
    path('workshops/', include('workshops.urls')),
]

# خدمة ملفات الـ media في الإنتاج والتطوير
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)