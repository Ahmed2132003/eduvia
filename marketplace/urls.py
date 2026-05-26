from django.urls import path

from .views import (
    ActivateCodeAPIView,
    MyEnrollmentsAPIView,
    AccessStatusAPIView,
    access_restricted_page,
    checkout_page,
    access_info_page,
    instructor_wallet_page,
    my_courses_page,
)

urlpatterns = [
    # ── API endpoints ─────────────────────────────────────────────────────────
    path("courses/<int:course_id>/activate-code/", ActivateCodeAPIView.as_view()),
    path("my/enrollments/", MyEnrollmentsAPIView.as_view()),
    path("my/access-status/", AccessStatusAPIView.as_view()),

    # ── HTML pages ────────────────────────────────────────────────────────────
    path("checkout/", checkout_page, name="marketplace_checkout"),
    path("access-restricted/", access_restricted_page, name="marketplace_access_restricted"),
    path("my/access-info/", access_info_page, name="marketplace_access_info"),
    path("my/courses/", my_courses_page, name="marketplace_my_courses"),
    path("wallet/", instructor_wallet_page, name="marketplace_instructor_wallet"),
]