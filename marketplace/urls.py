from django.urls import path

from .views import AccessStatusAPIView, ActivateCodeAPIView, CheckoutPaymobAPIView, MyEnrollmentsAPIView, PaymentWebhookAPIView, access_restricted_page, checkout_page

urlpatterns = [
    path("courses/<int:course_id>/checkout/paymob/", CheckoutPaymobAPIView.as_view()),
    path("courses/<int:course_id>/activate-code/", ActivateCodeAPIView.as_view()),
    path("payments/webhook/", PaymentWebhookAPIView.as_view()),
    path("my/enrollments/", MyEnrollmentsAPIView.as_view()),
    path("my/access-status/", AccessStatusAPIView.as_view()),
    path("checkout/", checkout_page, name="marketplace_checkout"),
    path("access-restricted/", access_restricted_page, name="marketplace_access_restricted"),
]