from django.urls import path

from .views import (
    # Existing API views
    AccessStatusAPIView,
    ActivateCodeAPIView,
    CheckoutPaymobAPIView,
    MyEnrollmentsAPIView,
    PaymentWebhookAPIView,
    # Existing HTML pages
    access_restricted_page,
    checkout_page,
    # New HTML pages
    access_info_page,
    instructor_wallet_page,
    my_courses_page,
)

urlpatterns = [
    # ── Existing API endpoints (unchanged) ───────────────────────────────────
    path("courses/<int:course_id>/checkout/paymob/", CheckoutPaymobAPIView.as_view()),
    path("courses/<int:course_id>/activate-code/", ActivateCodeAPIView.as_view()),
    path("payments/webhook/", PaymentWebhookAPIView.as_view()),
    path("my/enrollments/", MyEnrollmentsAPIView.as_view()),
    path("my/access-status/", AccessStatusAPIView.as_view()),
    # ── Existing HTML pages (unchanged) ──────────────────────────────────────
    path("checkout/", checkout_page, name="marketplace_checkout"),
    path(
        "access-restricted/",
        access_restricted_page,
        name="marketplace_access_restricted",
    ),
    # ── New HTML pages ────────────────────────────────────────────────────────
    path("my/access-info/", access_info_page, name="marketplace_access_info"),
    path("my/courses/", my_courses_page, name="marketplace_my_courses"),
    path("wallet/", instructor_wallet_page, name="marketplace_instructor_wallet"),
]