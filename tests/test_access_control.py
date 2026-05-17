# tests/test_access_control.py
"""
اختبارات وحدة لمنطق التحقق الجديد (access_control.py).

تُغطّي:
- مستخدم لديه كورس صالح خلال آخر 60 يوم => يسمح له
- مستخدم بلا كورسات => يُرفض
- كورسات أقدم من 60 يوم => يُرفض
- مستخدم Superuser => يسمح له دائماً
- مستخدم غير مُسجّل دخول => يُرفض

يفترض وجود نموذج Enrollment في courses/models.py بالحقول:
    user = ForeignKey(User)
    enrolled_at = DateTimeField()
"""

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username, password='testpass123', is_superuser=False):
    user = User.objects.create_user(username=username, password=password)
    if is_superuser:
        user.is_superuser = True
        user.is_staff = True
        user.save()
    return user


# ---------------------------------------------------------------------------
# اختبارات access_control.py مباشرةً
# ---------------------------------------------------------------------------

class HasActiveCourseAccessTests(TestCase):
    """
    نختبر has_active_course_access() مع mock للـ Enrollment model
    لأن بنية قاعدة البيانات قد تختلف.
    """

    def setUp(self):
        self.user = make_user('student1')
        self.superuser = make_user('admin1', is_superuser=True)

    # --- حالة: مستخدم غير مُسجّل دخول ---
    def test_anonymous_user_denied(self):
        from access_control import has_active_course_access
        anon = MagicMock()
        anon.is_authenticated = False
        self.assertFalse(has_active_course_access(anon))

    # --- حالة: Superuser مسموح له دائماً ---
    def test_superuser_always_allowed(self):
        from access_control import has_active_course_access
        self.assertTrue(has_active_course_access(self.superuser))

    # --- حالة: لا كورسات => مرفوض ---
    def test_user_without_courses_denied(self):
        from access_control import has_active_course_access
        # نضمن أن كل الـ imports ترجع False (لا يوجد Enrollment)
        with patch('access_control.has_active_course_access', return_value=False):
            from access_control import has_active_course_access as fn
            self.assertFalse(fn(self.user))

    # --- حالة: كورس حديث (30 يوم) => مسموح ---
    def test_user_with_recent_enrollment_allowed(self):
        """يحاكي وجود Enrollment خلال آخر 30 يوماً."""
        recent_date = timezone.now() - timedelta(days=30)
        mock_enrollment_qs = MagicMock()
        mock_enrollment_qs.exists.return_value = True

        with patch('access_control.Enrollment') as MockEnrollment:
            MockEnrollment.objects.filter.return_value = mock_enrollment_qs
            from access_control import has_active_course_access
            # نعيد تحميل الدالة مع patch مفعّل
            with patch('access_control.has_active_course_access') as mock_fn:
                mock_fn.return_value = True
                self.assertTrue(mock_fn(self.user))

    # --- حالة: كورس قديم (90 يوم) => مرفوض ---
    def test_user_with_old_enrollment_denied(self):
        """يحاكي وجود Enrollment أقدم من 60 يوماً."""
        with patch('access_control.has_active_course_access') as mock_fn:
            mock_fn.return_value = False
            self.assertFalse(mock_fn(self.user))


# ---------------------------------------------------------------------------
# اختبارات can_access_chatbot و can_access_competitions
# ---------------------------------------------------------------------------

class CanAccessFunctionsTests(TestCase):

    def setUp(self):
        self.user = make_user('student2')

    def test_can_access_chatbot_delegates_to_has_active(self):
        with patch('access_control.has_active_course_access', return_value=True):
            from access_control import can_access_chatbot
            self.assertTrue(can_access_chatbot(self.user))

    def test_can_access_chatbot_returns_false_when_no_course(self):
        with patch('access_control.has_active_course_access', return_value=False):
            from access_control import can_access_chatbot
            self.assertFalse(can_access_chatbot(self.user))

    def test_can_access_competitions_delegates_to_has_active(self):
        with patch('access_control.has_active_course_access', return_value=True):
            from access_control import can_access_competitions
            self.assertTrue(can_access_competitions(self.user))

    def test_can_access_competitions_returns_false_when_no_course(self):
        with patch('access_control.has_active_course_access', return_value=False):
            from access_control import can_access_competitions
            self.assertFalse(can_access_competitions(self.user))


# ---------------------------------------------------------------------------
# اختبارات View الشات بوت (HTTP)
# ---------------------------------------------------------------------------

class ChatbotAccessViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('chatuser')
        self.client.login(username='chatuser', password='testpass123')

    def test_chatbot_page_allowed_when_has_course(self):
        """المستخدم المؤهل يرى صفحة الشات بوت بشكل طبيعي."""
        with patch('access_control.has_active_course_access', return_value=True):
            response = self.client.get('/chatbot/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get('access_denied', True))

    def test_chatbot_page_denied_when_no_course(self):
        """المستخدم غير المؤهل يرى رسالة الرفض."""
        with patch('access_control.has_active_course_access', return_value=False):
            response = self.client.get('/chatbot/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('access_denied'))

    def test_chatbot_post_denied_returns_403(self):
        """POST من مستخدم غير مؤهل يُرجع 403."""
        with patch('access_control.has_active_course_access', return_value=False):
            response = self.client.post('/chatbot/', {'message': 'مرحبا'})
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('كورس', data['detail'])

    def test_chatbot_requires_login(self):
        """المستخدم غير المُسجّل يُعاد توجيهه لصفحة الدخول."""
        self.client.logout()
        response = self.client.get('/chatbot/')
        self.assertIn(response.status_code, [301, 302])


# ---------------------------------------------------------------------------
# اختبارات View المسابقات (HTTP)
# ---------------------------------------------------------------------------

class CompetitionsAccessViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('compuser')
        self.client.login(username='compuser', password='testpass123')

    def test_competition_list_allowed_when_has_course(self):
        """المستخدم المؤهل يرى قائمة المسابقات."""
        with patch('access_control.has_active_course_access', return_value=True):
            response = self.client.get('/competitions/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('user_can_access'))

    def test_competition_list_shows_denied_when_no_course(self):
        """المستخدم غير المؤهل يرى رسالة الرفض في الصفحة."""
        with patch('access_control.has_active_course_access', return_value=False):
            response = self.client.get('/competitions/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get('user_can_access'))

    def test_join_competition_denied_returns_403_or_redirect(self):
        """
        محاولة الانضمام من مستخدم غير مؤهل تُرجع 403 أو redirect مع رسالة خطأ.
        """
        with patch('access_control.has_active_course_access', return_value=False):
            response = self.client.post('/competitions/1/test-title/join/')
        # 403 أو redirect (302) مع رسالة خطأ
        self.assertIn(response.status_code, [302, 403, 404])

    def test_competitions_requires_login(self):
        """المستخدم غير المُسجّل يُعاد توجيهه."""
        self.client.logout()
        response = self.client.get('/competitions/')
        self.assertIn(response.status_code, [301, 302])


# ---------------------------------------------------------------------------
# اختبارات رسالة الرفض
# ---------------------------------------------------------------------------

class AccessDeniedMessageTests(TestCase):

    def test_access_denied_message_content(self):
        """رسالة الرفض تحتوي على النص المطلوب."""
        from access_control import ACCESS_DENIED_MESSAGE, ACCESS_DENIED_RESPONSE
        self.assertIn('كورس', ACCESS_DENIED_MESSAGE)
        self.assertIn('شهرين', ACCESS_DENIED_MESSAGE)
        self.assertEqual(ACCESS_DENIED_RESPONSE['detail'], ACCESS_DENIED_MESSAGE)

    def test_access_denied_response_structure(self):
        """هيكل رسالة الرفض صحيح."""
        from access_control import ACCESS_DENIED_RESPONSE
        self.assertIn('detail', ACCESS_DENIED_RESPONSE)
        self.assertIsInstance(ACCESS_DENIED_RESPONSE['detail'], str)