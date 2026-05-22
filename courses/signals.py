from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, profile_created = UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'student', 'coins': 300}
        )
        # إذا كان المستخدم إنستراكتور، فعّل is_staff
        if hasattr(instance, 'role') and instance.role == 'instructor':
            instance.is_staff = True
            instance.is_active = True
            instance.save()
            profile.role = 'instructor'
            profile.save()
    else:
        # تحديث is_staff لو الدور اتغيّر، لكن تجاهل لو المستخدم superuser
        try:
            profile = instance.courses_profile
            if not instance.is_superuser:  # إضافة الشرط ده
                if profile.role == 'instructor' and not instance.is_staff:
                    instance.is_staff = True
                    instance.is_active = True
                    instance.save()
                elif profile.role != 'instructor' and instance.is_staff:
                    instance.is_staff = False
                    instance.save()
        except UserProfile.DoesNotExist:
            pass
        
from django.db.models.signals import post_save, post_delete
 
@receiver(post_save, sender=LessonRating)
@receiver(post_delete, sender=LessonRating)
def recalculate_course_average_rating(sender, instance, **kwargs):
    """
    After any LessonRating is saved or deleted, recompute the parent
    Course.average_rating from all ratings in that course.
    Uses a single aggregation query — safe & optimised.
    """
    from django.db.models import Avg
    course = instance.lesson.section.course
    result = LessonRating.objects.filter(
        lesson__section__course=course
    ).aggregate(avg=Avg('rating'))
    course.average_rating = round(result['avg'] or 0, 2)
    course.save(update_fields=['average_rating'])
