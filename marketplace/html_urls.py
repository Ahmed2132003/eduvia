"""
marketplace/html_urls.py
========================
Short /marketplace/... URLs for the 3 HTML pages.
Mounted at  marketplace/  in Eduvia/urls.py
No name conflicts with api/marketplace/ because names here have _html suffix.
"""
from django.urls import path
from .views import access_info_page, instructor_wallet_page, my_courses_page

urlpatterns = [
    path("access-restricted/", access_info_page,        name="marketplace_access_info_html"),
    path("wallet/",            instructor_wallet_page,   name="marketplace_wallet_html"),
    path("my-courses/",        my_courses_page,          name="marketplace_my_courses_html"),
]