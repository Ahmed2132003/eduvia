"""
tests/test_access.py
=====================
اختبارات منطق الوصول الجديد (بدون نظام اشتراكات).
"""

from unittest.mock import patch, MagicMock, PropertyMock

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class HasRecentCourseAccessTests(TestCase):
    """اختبارات دالة has_recent_course_access."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@test.com'
        )

    # ------------------------------------------------------------------
    # حالات النجاح
    # ------------------------------------------------------------------

    def test_user_with_enrollment_within_60_days_has_access(self):
        """مستخدم لديه تسجيل خلال آخر 60 يوم => يُسمح له."""
        import core.access as access_module
        from core.access import has_recent_course_access

        mock_manager = MagicMock()
        mock_manager.filter.return_value.exists.return_value = True

        original = access_module.CourseEnrollment
        try:
            mock_model = MagicMock()
            mock_model.objects = mock_manager
            access_module.CourseEnrollment = mock_model
            result = has_recent_course_access(self.user)
        finally:
            access_module.CourseEnrollment = original

        self.assertTrue(result)

    def test_superuser_always_has_access(self):
        """المسؤول (superuser) دائمًا مسموح له."""
        from core.access import has_recent_course_access

        self.user.is_superuser = True
        self.user.save()
        # أعِد تحميل المستخدم من DB
        user = User.objects.get(pk=self.user.pk)
        result = has_recent_course_access(user)
        self.assertTrue(result)

    def test_staff_always_has_access(self):
        """staff دائمًا مسموح له."""
        from core.access import has_recent_course_access

        # update مباشر في DB لتجاوز أي override في الـ custom User model
        User.objects.filter(pk=self.user.pk).update(is_staff=True)
        user = User.objects.get(pk=self.user.pk)
        result = has_recent_course_access(user)
        self.assertTrue(result)

    def test_user_with_video_progress_within_60_days(self):
        """مستخدم لديه نشاط فيديو حديث => يُسمح له."""
        import core.access as access_module
        from core.access import has_recent_course_access

        # CourseEnrollment لا يُعيد شيئًا
        mock_enrollment = MagicMock()
        mock_enrollment.objects.filter.return_value.exists.return_value = False

        # VideoProgress يُعيد نتيجة
        mock_progress = MagicMock()
        mock_progress.objects.filter.return_value.exists.return_value = True

        original_enrollment = access_module.CourseEnrollment
        original_progress = access_module.VideoProgress
        try:
            access_module.CourseEnrollment = mock_enrollment
            access_module.VideoProgress = mock_progress
            result = has_recent_course_access(self.user)
        finally:
            access_module.CourseEnrollment = original_enrollment
            access_module.VideoProgress = original_progress

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
        import core.access as access_module
        from core.access import has_recent_course_access

        mock_enrollment = MagicMock()
        mock_enrollment.objects.filter.return_value.exists.return_value = False

        mock_progress = MagicMock()
        mock_progress.objects.filter.return_value.exists.return_value = False

        original_enrollment = access_module.CourseEnrollment
        original_progress = access_module.VideoProgress
        try:
            access_module.CourseEnrollment = mock_enrollment
            access_module.VideoProgress = mock_progress
            result = has_recent_course_access(self.user)
        finally:
            access_module.CourseEnrollment = original_enrollment
            access_module.VideoProgress = original_progress

        self.assertFalse(result)

    def test_user_with_old_enrollment_has_no_access(self):
        """مستخدم لديه تسجيل أقدم من 60 يوم => مرفوض."""
        import core.access as access_module
        from core.access import has_recent_course_access

        # الفلتر بتاريخ آخر 60 يوم لا يُعيد شيئًا
        mock_enrollment = MagicMock()
        mock_enrollment.objects.filter.return_value.exists.return_value = False

        mock_progress = MagicMock()
        mock_progress.objects.filter.return_value.exists.return_value = False

        original_enrollment = access_module.CourseEnrollment
        original_progress = access_module.VideoProgress
        try:
            access_module.CourseEnrollment = mock_enrollment
            access_module.VideoProgress = mock_progress
            result = has_recent_course_access(self.user)
        finally:
            access_module.CourseEnrollment = original_enrollment
            access_module.VideoProgress = original_progress

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
        self.assertIn(response.status_code, [302, 404])

    def test_access_denied_message_content(self):
        """رسالة الرفض تحتوي على '60' و'كورس'."""
        from core.access import ACCESS_DENIED_MESSAGE
        self.assertIn('60', ACCESS_DENIED_MESSAGE)
        self.assertIn('كورس', ACCESS_DENIED_MESSAGE)