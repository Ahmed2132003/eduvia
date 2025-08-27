# accounts/management/commands/calculate_payouts.py
from django.core.management.base import BaseCommand
from accounts.models import Profile, InstructorPayout
from courses.models import Course
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Calculate and distribute instructor payouts'

    def handle(self, *args, **kwargs):
        # جمع إجمالي الإيرادات من الاشتراكات بالجنيه المصري
        total_revenue = 0
        profiles = Profile.objects.exclude(subscription_plan='free')
        for profile in profiles:
            if profile.subscription_plan == 'basic':
                total_revenue += 150  # أو 135 أو 120 بناءً على المدة
            elif profile.subscription_plan == 'pro':
                total_revenue += 350  # أو 315 أو 280
            elif profile.subscription_plan == 'premium':
                total_revenue += 500  # أو 450 أو 400
            elif profile.subscription_plan == 'instructor':
                total_revenue += 400  # أو 360 أو 320

        # خصم رسوم Paymob (تقريبًا 2.5% + 3 جنيه لكل معاملة)
        paymob_fee = (total_revenue * 0.025) + (3 * profiles.count())
        net_revenue = total_revenue - paymob_fee
        instructor_share = net_revenue * 0.5  # 50% للمحاضرين

        # جمع إجمالي المشاهدات
        total_views = Course.objects.aggregate(Sum('views'))['views__sum'] or 0
        if total_views == 0:
            return

        # توزيع الأرباح بناءً على المشاهدات
        instructors = Profile.objects.filter(subscription_plan='instructor')
        for instructor_profile in instructors:
            instructor_courses = Course.objects.filter(instructor=instructor_profile.user)
            instructor_views = instructor_courses.aggregate(Sum('views'))['views__sum'] or 0
            payout_percentage = instructor_views / total_views if total_views > 0 else 0
            payout_amount = instructor_share * payout_percentage
            if payout_percentage > 0.1:  # أكثر من 10% من المشاهدات
                payout_amount *= 1.05  # بونص 5%

            # إنشاء سجل دفع
            InstructorPayout.objects.create(
                instructor=instructor_profile.user,
                amount=payout_amount,
                course_views=instructor_views,
                total_platform_views=total_views,
                payout_percentage=payout_percentage
            )
            self.stdout.write(self.style.SUCCESS(f'Payout of EGP {payout_amount:.2f} to {instructor_profile.user.username}'))