"""
groups/live_provider.py
========================
Part 23 (المرحلة الثانية — البث المباشر): طبقة اتصال معزولة بمزود الـ
WebRTC (LiveKit) اللي اتقرر في Part 22 (تفاصيل القرار المعماري الكاملة
في PROGRESS_PART22.md).

الملف ده مقصود يكون معزول تمامًا عن groups/views.py — أي view هيستخدم
البث المباشر (Part 24/25) المفروض ينادي بس على الدوال التلاتة هنا
(create_room / generate_access_token / end_room) من غير ما يعرف أي
تفصيلة عن LiveKit SDK نفسه. لو يومًا ما احتجنا نغيّر المزود (Jitsi
مثلاً)، التغيير كله هيبقى محصور في الملف ده بس.

ملحوظة (Part 26 — نسخة معدّلة): الملف ده كان فيه كمان منطق تفعيل تسجيل
تلقائي (LiveKit Egress -> S3) بينادى من جوه create_room(). المنطق ده
اتلغى بالكامل — التسجيل بقى مسؤولية المدرس (رفع يدوي بعد انتهاء اللايف)،
مش حاجة بتحصل تلقائيًا وقت إنشاء الروم. create_room() رجعت لمسؤوليتها
الأصلية بس: إنشاء الروم عند LiveKit.

قرار تقني مهم: livekit-api (Server SDK الرسمي، Python) كله async
بالكامل (مبني على aiohttp) — تأكدت من ده فعليًا بتثبيت المكتبة ومراجعة
توقيعات الدوال (AccessToken، VideoGrants، LiveKitAPI.room.create_room/
delete_room) قبل ما أكتب أي كود، بدل ما أفترض شكل الـ API من الذاكرة.
باقي المشروع كله sync (function-based views عادية، زي كل حتة في
groups/workshops) فمفيش داعي نحول أي حاجة لـ async — كل دالة هنا سنكرونية
عادية، وبتلف نداء LiveKit جوه asyncio.run() داخليًا بس.
"""
import asyncio
import logging
import uuid
from datetime import timedelta

from django.conf import settings

from livekit import api as lk_api

logger = logging.getLogger(__name__)


class LiveProviderError(Exception):
    """
    خطأ عام أثناء التواصل مع مزود البث (LiveKit) — إعدادات ناقصة، أو
    فشل فعلي في نداء الـ API. أي view بينادي على دوال الملف ده لازم
    يمسك الاستثناء ده (try/except) ويعرض رسالة واضحة للمستخدم بدل ما
    يسيب الصفحة تطلع بـ 500 خام.
    """
    pass


# مدة صلاحية أي access token بيتولّد — 6 ساعات كافية لأي جلسة لايف
# طويلة، من غير ما نسيب توكن صالح لمدة غير محدودة لو اتسرب بالغلط.
_TOKEN_TTL = timedelta(hours=6)

# لو الروم فاضي (مفيش حد متصل) لمدة الوقت ده، LiveKit بيقفله تلقائيًا
# من نفسه — طبقة حماية إضافية بعيدًا عن end_room الصريحة (Part 24).
_EMPTY_ROOM_TIMEOUT_SECONDS = 60 * 60  # ساعة


def _require_provider_settings():
    if not (settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY and settings.LIVEKIT_API_SECRET):
        raise LiveProviderError(
            "إعدادات LiveKit (LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET) "
            "مش مظبوطة كمتغيرات بيئة — راجع Eduvia/settings.py وPart 23 في PROGRESS."
        )


def _get_client():
    _require_provider_settings()
    return lk_api.LiveKitAPI(
        settings.LIVEKIT_URL,
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET,
    )


def _run(coro):
    """تشغيل coroutine واحدة من غير ما نضطر نحول الملف كله لـ async."""
    return asyncio.run(coro)


def _room_name_for(session):
    """
    اسم روم فريد عند LiveKit — مبني على id الجروب وid الجلسة، زائد جزء
    عشوائي قصير عشان يمنع أي تعارض نظري لو نفس session اتعمله create_room
    أكتر من مرة (مثلاً بعد فشل جزئي وإعادة محاولة).
    """
    return f"group-{session.group_id}-live-{session.pk or 'new'}-{uuid.uuid4().hex[:8]}"


def create_room(session):
    """
    بينشئ روم جديد فعليًا عند LiveKit للجلسة دي (GroupLiveSession)،
    ويرجع الـ room_identifier (نص) — القيمة دي المفروض تتحفظ في
    session.room_identifier من الـ view اللي بينادي الدالة دي (Part 24).

    ملحوظة (Part 26 — نسخة معدّلة): كانت الدالة دي بتفعّل تسجيل تلقائي
    (LiveKit Egress -> S3) بعد نجاح إنشاء الروم — ده اتلغى بالكامل.
    التسجيل بقى مسؤولية المدرس بالكامل (رفع يدوي بعد ما اللايف يخلص، عن
    طريق groups/views.py::upload_group_recording)، فالدالة دي رجعت
    تعمل حاجة واحدة بس: تنشئ الروم. تفاصيل القرار في PROGRESS.

    ملحوظة: الدالة دي مبتحفظش الـ session بنفسها (مفيش .save() هنا) —
    عشان تفضل معزولة تمامًا عن أي منطق Django ORM/views، ومسؤولية الحفظ
    بتفضل للـ caller.
    """
    room_name = _room_name_for(session)

    async def _create():
        client = _get_client()
        try:
            await client.room.create_room(
                lk_api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=_EMPTY_ROOM_TIMEOUT_SECONDS,
                    max_participants=0,  # 0 = من غير حد أقصى (LiveKit SFU بيتحمل)
                )
            )
        finally:
            await client.aclose()

    try:
        _run(_create())
    except LiveProviderError:
        raise
    except Exception as exc:
        logger.exception("LiveKit create_room فشلت للجلسة id=%s", session.pk)
        raise LiveProviderError(f"فشل إنشاء الروم عند LiveKit: {exc}") from exc

    return room_name


def generate_access_token(session, user, role='viewer'):
    """
    بيولّد JWT access token يستخدمه الـ Client SDK (JS، هيتضاف في
    Part 24/25) عشان يتصل مباشرة بسيرفر LiveKit — الـ Django backend مش
    جزء من مسار الميديا خالص، دوره بس فحص الصلاحية (بيحصل في الـ view
    قبل ما توصل هنا — is_group_content_accessible / GroupMembership من
    Part 15/25) وتوليد التوكن بس.

    role='host'   -> صاحب الجلسة (المدرس): يقدر ينشر كاميرا/مشاركة شاشة
                      (can_publish=True).
    role='viewer' -> الطالب: مشاهدة بس، من غير أي صلاحية نشر
                      (can_publish=False).
    """
    if role not in ('host', 'viewer'):
        raise LiveProviderError(f"role غير معروف: {role!r} — لازم يكون 'host' أو 'viewer'.")

    if not session.room_identifier:
        raise LiveProviderError(
            "الجلسة دي لسه معملهاش روم عند LiveKit (room_identifier فاضي) — "
            "نادي create_room() الأول."
        )

    _require_provider_settings()

    is_host = role == 'host'
    grants = lk_api.VideoGrants(
        room_join=True,
        room=session.room_identifier,
        can_publish=is_host,
        can_publish_data=True,
        can_subscribe=True,
    )

    display_name = user.get_full_name() or user.username

    token = (
        lk_api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        .with_identity(f"user-{user.pk}")
        .with_name(display_name)
        .with_ttl(_TOKEN_TTL)
        .with_grants(grants)
    )

    return token.to_jwt()


def end_room(session):
    """
    بيقفل الروم عند LiveKit فعليًا (بيفصل كل المشاركين المتصلين دلوقتي،
    لو فيه). لو الروم مش موجود أصلاً عند المزود (اتقفل لوحده بسبب
    empty_timeout مثلاً، أو اتقفل قبل كده)، بنسجل تحذير في اللوج بدل ما
    نرمي استثناء يوقف الـ view اللي بينادينا — النتيجة النهائية المطلوبة
    (الروم مقفول) متحققة أصلاً في الحالة دي.
    """
    if not session.room_identifier:
        return

    async def _end():
        client = _get_client()
        try:
            await client.room.delete_room(
                lk_api.DeleteRoomRequest(room=session.room_identifier)
            )
        finally:
            await client.aclose()

    try:
        _run(_end())
    except LiveProviderError:
        raise
    except Exception:
        logger.warning(
            "LiveKit end_room: الروم %s ممكن يكون مقفول بالفعل عند المزود "
            "(اتجاهل الخطأ لأن النتيجة النهائية المطلوبة متحققة).",
            session.room_identifier,
            exc_info=True,
        )