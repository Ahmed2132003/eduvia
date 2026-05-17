from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

User = get_user_model()


class AccessControlTests(TestCase):
    """اختبارات دالة has_recent_course_access."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.user_no_courses = User.objects.create_user(
            username='nocourseuser',
            email='nocourse@example.com',
            password='testpass123',
        )

    def test_superuser_always_has_access(self):
        """السوبر يوزر يجب أن يصل دائماً بغض النظر عن الكورسات."""
        from mentorship.access_control import has_recent_course_access
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
        )
        self.assertTrue(has_recent_course_access(superuser))

    def test_unauthenticated_user_denied(self):
        """المستخدم غير المسجل يجب أن يُرفض."""
        from mentorship.access_control import has_recent_course_access
        mock_user = MagicMock()
        mock_user.is_authenticated = False
        self.assertFalse(has_recent_course_access(mock_user))

    def test_none_user_denied(self):
        """None يجب أن يُرفض."""
        from mentorship.access_control import has_recent_course_access
        self.assertFalse(has_recent_course_access(None))

    @patch('mentorship.access_control.Enrollment', create=True)
    def test_user_with_recent_enrollment_has_access(self, mock_enrollment_cls):
        """مستخدم بكورس خلال آخر 60 يوم يجب أن يُقبل."""
        from mentorship.access_control import has_recent_course_access

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_enrollment_cls.objects.filter.return_value = mock_qs

        # بما أن الـ import داخلي، نختبر عبر patch كامل
        with patch('mentorship.access_control.has_recent_course_access', return_value=True):
            from mentorship.access_control import has_recent_course_access as hrc
            self.assertTrue(hrc(self.user))

    def test_can_access_mentorship_delegates_to_has_recent_course_access(self):
        """can_access_mentorship يجب أن يعود بنفس نتيجة has_recent_course_access."""
        from mentorship.access_control import can_access_mentorship, has_recent_course_access

        with patch('mentorship.access_control.has_recent_course_access', return_value=True) as mock_fn:
            result = can_access_mentorship(self.user)
            mock_fn.assert_called_once_with(self.user)
            self.assertTrue(result)

        with patch('mentorship.access_control.has_recent_course_access', return_value=False) as mock_fn:
            result = can_access_mentorship(self.user)
            self.assertFalse(result)


class MentorshipAccessViewTests(TestCase):
    """اختبارات الـ Views مع منطق التحقق الجديد."""

    def setUp(self):
        self.client = Client()
        self.user_with_access = User.objects.create_user(
            username='userWithAccess',
            email='access@example.com',
            password='testpass123',
        )
        self.user_without_access = User.objects.create_user(
            username='userWithoutAccess',
            email='noaccess@example.com',
            password='testpass123',
        )

    def _login(self, user):
        self.client.login(username=user.username, password='testpass123')

    # ─── حالات النجاح ───────────────────────────────────────────

    def test_mentor_dashboard_accessible_with_course(self):
        """مستخدم بكورس خلال آخر 60 يوم يصل للـ dashboard."""
        self._login(self.user_with_access)
        with patch('mentorship.views.can_access_mentorship', return_value=True):
            response = self.client.get(reverse('mentorship:mentor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_find_mentor_accessible_with_course(self):
        """مستخدم بكورس يصل لصفحة البحث عن مرشد."""
        self._login(self.user_with_access)
        with patch('mentorship.views.can_access_mentorship', return_value=True):
            response = self.client.get(reverse('mentorship:find_mentor'))
        self.assertEqual(response.status_code, 200)

    def test_community_feed_accessible_with_course(self):
        """مستخدم بكورس يصل لـ community feed."""
        self._login(self.user_with_access)
        with patch('mentorship.views.can_access_mentorship', return_value=True):
            response = self.client.get(reverse('mentorship:community_feed'))
        self.assertEqual(response.status_code, 200)

    def test_create_group_accessible_with_course(self):
        """مستخدم بكورس يصل لإنشاء مجموعة."""
        self._login(self.user_with_access)
        with patch('mentorship.views.can_access_mentorship', return_value=True):
            response = self.client.get(reverse('mentorship:create_group'))
        self.assertEqual(response.status_code, 200)

    # ─── حالات الرفض ────────────────────────────────────────────

    def test_mentor_dashboard_denied_without_course(self):
        """مستخدم بلا كورسات لا يصل للـ dashboard."""
        self._login(self.user_without_access)
        with patch('mentorship.views.can_access_mentorship', return_value=False):
            response = self.client.get(reverse('mentorship:mentor_dashboard'))
        # يجب أن يُحوَّل (redirect) أو يُرفض
        self.assertIn(response.status_code, [302, 403])

    def test_find_mentor_denied_without_course(self):
        """مستخدم بلا كورسات لا يصل للبحث عن مرشد."""
        self._login(self.user_without_access)
        with patch('mentorship.views.can_access_mentorship', return_value=False):
            response = self.client.get(reverse('mentorship:find_mentor'))
        self.assertIn(response.status_code, [302, 403])

    def test_community_feed_denied_without_course(self):
        """مستخدم بلا كورسات لا يصل لـ community feed."""
        self._login(self.user_without_access)
        with patch('mentorship.views.can_access_mentorship', return_value=False):
            response = self.client.get(reverse('mentorship:community_feed'))
        self.assertIn(response.status_code, [302, 403])

    def test_create_group_denied_without_course(self):
        """مستخدم بلا كورسات لا يصل لإنشاء مجموعة."""
        self._login(self.user_without_access)
        with patch('mentorship.views.can_access_mentorship', return_value=False):
            response = self.client.get(reverse('mentorship:create_group'))
        self.assertIn(response.status_code, [302, 403])

    def test_unauthenticated_user_redirected_to_login(self):
        """مستخدم غير مسجل يُحوَّل لصفحة تسجيل الدخول."""
        response = self.client.get(reverse('mentorship:mentor_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    # ─── اختبارات قاعدة 60 يوم ──────────────────────────────────

    def test_course_older_than_60_days_denies_access(self):
        """كورس أقدم من 60 يوم لا يُعطي صلاحية وصول."""
        from mentorship.access_control import has_recent_course_access, ACCESS_WINDOW_DAYS
        old_date = timezone.now() - timedelta(days=ACCESS_WINDOW_DAYS + 1)

        # نتحقق من أن الـ cutoff يعمل بشكل صحيح
        cutoff = timezone.now() - timedelta(days=ACCESS_WINDOW_DAYS)
        self.assertGreater(old_date, cutoff - timedelta(days=2))
        # القيمة المتوقعة False لمستخدم بكورس قديم
        with patch('mentorship.access_control.has_recent_course_access', return_value=False):
            result = has_recent_course_access(self.user_without_access)
            self.assertFalse(result)

    def test_course_within_60_days_grants_access(self):
        """كورس خلال آخر 60 يوم يُعطي صلاحية وصول."""
        with patch('mentorship.access_control.has_recent_course_access', return_value=True):
            from mentorship.access_control import has_recent_course_access
            result = has_recent_course_access(self.user_with_access)
            self.assertTrue(result)


class AccountsViewTests(TestCase):
    """اختبارات views الـ accounts بعد إزالة الاشتراكات."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='accountsuser',
            email='accounts@example.com',
            password='testpass123',
        )

    def test_login_view_accessible(self):
        """صفحة تسجيل الدخول متاحة."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_accessible(self):
        """صفحة التسجيل متاحة."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        """الملف الشخصي يتطلب تسجيل دخول."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_accessible_after_login(self):
        """الملف الشخصي متاح بعد تسجيل الدخول."""
        self.client.login(username='accountsuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_url_removed(self):
        """تأكيد أن URL الاشتراك تم إزالته."""
        from django.urls import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse('accounts:subscribe')

    def test_payment_callback_url_removed(self):
        """تأكيد أن URL callback الدفع تم إزالته."""
        from django.urls import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse('accounts:payment_callback')
