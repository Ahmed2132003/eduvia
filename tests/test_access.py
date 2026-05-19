"""
tests/test_access.py
=====================
اختبارات منطق الوصول الجديد (بدون نظام اشتراكات).
"""

from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()


class HasRecentCourseAccessTests(TestCase):
    """اختبارات دالة has_recent_course_access."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@test.com'
        )
        self.factory = RequestFactory()

    # ------------------------------------------------------------------
    # حالات النجاح
    # ------------------------------------------------------------------

    def test_user_with_enrollment_within_60_days_has_access(self):
        """مستخدم لديه تسجيل خلال آخر 60 يوم => يُسمح له."""
        from core.access import has_recent_course_access

        mock_qs = MagicMock()
        mock_qs.filter.return_value.exists.return_value = True

        with patch('core.access.CourseEnrollment.objects', mock_qs):
            result = has_recent_course_access(self.user)

        self.assertTrue(result)

    def test_superuser_always_has_access(self):
        """المسؤول (superuser) دائمًا مسموح له."""
        from core.access import has_recent_course_access

        self.user.is_superuser = True
        self.user.save()
        result = has_recent_course_access(self.user)
        self.assertTrue(result)

    def test_staff_always_has_access(self):
        """staff دائمًا مسموح له."""
        from core.access import has_recent_course_access

        self.user.is_staff = True
        self.user.save()
        result = has_recent_course_access(self.user)
        self.assertTrue(result)

    def test_user_with_video_progress_within_60_days(self):
        """مستخدم لديه نشاط فيديو حديث => يُسمح له."""
        from core.access import has_recent_course_access

        mock_enrollment_qs = MagicMock()
        mock_enrollment_qs.filter.return_value.exists.return_value = False

        mock_progress_qs = MagicMock()
        mock_progress_qs.filter.return_value.exists.return_value = True

        with patch('core.access.CourseEnrollment.objects', mock_enrollment_qs), \
             patch('core.access.VideoProgress.objects', mock_progress_qs):
            result = has_recent_course_access(self.user)

        self.assertTrue(result)

    # ------------------------------------------------------------------
    # حالات الرفض
    # ------------------------------------------------------------------

    def test_unauthenticated_user_has_no_access(self):
        """مستخدم غير مسجَّل دخول => مرفوض."""
        from core.access import has_recent_course_access

        anonymous = MagicMock()
        anonymous.is_authenticated = False
        result = has_recent_course_access(anonymous)
        self.assertFalse(result)

    def test_none_user_has_no_access(self):
        """None => مرفوض."""
        from core.access import has_recent_course_access

        result = has_recent_course_access(None)
        self.assertFalse(result)

    def test_user_with_no_courses_has_no_access(self):
        """مستخدم بلا كورسات => مرفوض."""
        from core.access import has_recent_course_access

        mock_qs = MagicMock()
        mock_qs.filter.return_value.exists.return_value = False

        with patch('core.access.CourseEnrollment.objects', mock_qs), \
             patch('core.access.VideoProgress.objects', mock_qs):
            result = has_recent_course_access(self.user)

        self.assertFalse(result)

    def test_user_with_old_enrollment_has_no_access(self):
        """مستخدم لديه تسجيل أقدم من 60 يوم => مرفوض."""
        from core.access import has_recent_course_access

        # نحاكي أن الفلتر بتاريخ آخر 60 يوم لا يُعيد شيئًا
        mock_qs = MagicMock()
        mock_qs.filter.return_value.exists.return_value = False

        with patch('core.access.CourseEnrollment.objects', mock_qs), \
             patch('core.access.VideoProgress.objects', mock_qs):
            result = has_recent_course_access(self.user)

        self.assertFalse(result)

    # ------------------------------------------------------------------
    # اختبارات دوال الوصول المتخصصة
    # ------------------------------------------------------------------

    def test_can_access_performance_analysis_delegates(self):
        """can_access_performance_analysis تفوِّض لـ has_recent_course_access."""
        from core.access import can_access_performance_analysis

        with patch('core.access.has_recent_course_access', return_value=True) as mock:
            result = can_access_performance_analysis(self.user)
            mock.assert_called_once_with(self.user)
        self.assertTrue(result)

    def test_can_access_projects_delegates(self):
        """can_access_projects تفوِّض لـ has_recent_course_access."""
        from core.access import can_access_projects

        with patch('core.access.has_recent_course_access', return_value=False) as mock:
            result = can_access_projects(self.user)
            mock.assert_called_once_with(self.user)
        self.assertFalse(result)

    def test_can_access_skills_market_delegates(self):
        """can_access_skills_market تفوِّض لـ has_recent_course_access."""
        from core.access import can_access_skills_market

        with patch('core.access.has_recent_course_access', return_value=True) as mock:
            result = can_access_skills_market(self.user)
            mock.assert_called_once_with(self.user)
        self.assertTrue(result)

    def test_can_access_workshops_delegates(self):
        """can_access_workshops تفوِّض لـ has_recent_course_access."""
        from core.access import can_access_workshops

        with patch('core.access.has_recent_course_access', return_value=False) as mock:
            result = can_access_workshops(self.user)
            mock.assert_called_once_with(self.user)
        self.assertFalse(result)


class AccessDeniedResponseTests(TestCase):
    """اختبارات رسالة الرفض وحماية الـ Views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='nocoursesuser', password='pass', email='no@test.com'
        )
        self.client.login(username='nocoursesuser', password='pass')

    def test_performance_dashboard_returns_403_for_api_request(self):
        """Dashboard يُرجع 403 JSON لمستخدم غير مؤهل عند طلب API."""
        with patch('core.access.has_recent_course_access', return_value=False):
            response = self.client.get(
                '/performance/dashboard/',
                HTTP_ACCEPT='application/json',
            )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('كورس', data['detail'])

    def test_projects_view_redirects_for_html_request(self):
        """Projects تُعيد redirect لمستخدم غير مؤهل عند طلب HTML."""
        with patch('core.access.has_recent_course_access', return_value=False):
            response = self.client.get('/projects/project/1/test-project/')
        # يجب أن يُعيد redirect (302) أو الصفحة الرئيسية
        self.assertIn(response.status_code, [302, 404])

    def test_access_denied_message_content(self):
        """رسالة الرفض تحتوي على النص الصحيح."""
        from core.access import ACCESS_DENIED_MESSAGE
        self.assertIn('60', ACCESS_DENIED_MESSAGE)
        self.assertIn('كورس', ACCESS_DENIED_MESSAGE)