from django.urls import path
from .views import (
    BuyCourseAPIView,
    ApplyEnrollmentCodeAPIView,
    MyCoursesAPIView,
    InstructorEarningsAPIView,
    checkout_page,
    my_courses_page,
    access_restricted_page,
    instructor_wallet_page,
)

urlpatterns = [
    path('student/buy-course/', BuyCourseAPIView.as_view()),
    path('student/apply-code/', ApplyEnrollmentCodeAPIView.as_view()),
    path('student/my-courses/', MyCoursesAPIView.as_view()),
    path('instructor/earnings/', InstructorEarningsAPIView.as_view()),
    path('checkout/', checkout_page, name='marketplace_checkout'),
    path('my-courses/', my_courses_page, name='marketplace_my_courses'),
    path('access-restricted/', access_restricted_page, name='marketplace_access_restricted'),
    path('instructor/wallet/', instructor_wallet_page, name='marketplace_instructor_wallet'),
]