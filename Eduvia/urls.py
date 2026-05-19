from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls, name='admin_dashboard'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('healthcheck/', health_check),
    path('', include('pages.urls')),
    path('courses/', include('courses.urls')),
    path("chatbot/", include("chatbot.urls")),
    path("competitions/", include("competitions.urls")),
    path('performance/', include('performance_analysis.urls')),
    path('projects/', include('projects.urls')),
    path('skills_market/', include('skills_market.urls')),
    path("mentorship/", include("mentorship.urls")),
    path('workshops/', include('workshops.urls')),

    # ── API namespace (existing — untouched) ──────────────────────────────────
    path('api/marketplace/', include('marketplace.urls')),

    # ── Friendly HTML URLs  /marketplace/...  ────────────────────────────────
    # Uses a separate urls file to avoid name conflicts.
    # Gives you:
    #   /marketplace/access-restricted/
    #   /marketplace/wallet/
    #   /marketplace/my-courses/
    path('marketplace/', include('marketplace.html_urls')),
]

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)