from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Mentorship, MentorshipGroup, GroupRequest,
    GroupChat, GroupMessage, MentorRating, Post, Comment
)
from .forms import MentorshipGroupForm, GroupMessageForm, MentorRatingForm, AddMemberForm
from courses.models import UserProfile
from .access_control import (
    can_access_mentorship,
    ACCESS_DENIED_MESSAGE,
)

import re


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def clean_text(text):
    """تحويل النص إلى slug آمن للـ URL."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text


def _deny_access(request):
    """رد 403 موحد لجميع نقاط الرفض."""
    messages.error(request, ACCESS_DENIED_MESSAGE)
    return redirect('home')


# ─────────────────────────────────────────────
# Mentor / Mentee Views
# ─────────────────────────────────────────────

@login_required
def become_mentor(request):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.role == 'student':
        profile.role = 'instructor'
        profile.save()
        messages.success(request, "أنت الآن مرشد!")
    return redirect('mentorship:mentor_dashboard')


@login_required
def mentor_dashboard(request):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    user = request.user
    mentees = Mentorship.objects.filter(mentor=user, is_active=True)
    admin_groups = MentorshipGroup.objects.filter(admin=user)
    member_groups = user.mentorship_groups.all()

    return render(request, 'mentorship/mentor_dashboard.html', {
        'mentees': mentees,
        'admin_groups': admin_groups,
        'member_groups': member_groups,
        'can_create_group': True,
        'current_admin': admin_groups.count(),
        'current_member': member_groups.exclude(admin=user).count(),
    })


@login_required
def find_mentor(request):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    User = get_user_model()
    mentors = User.objects.filter(courses_profile__role='instructor')
    public_groups = MentorshipGroup.objects.filter(
        is_public=True
    ).exclude(members=request.user)
    private_groups = MentorshipGroup.objects.filter(
        is_public=False
    ).exclude(members=request.user)

    return render(request, 'mentorship/find_mentor.html', {
        'mentors': mentors,
        'public_groups': public_groups,
        'private_groups': private_groups,
    })


@login_required
def request_mentorship(request, mentor_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    User = get_user_model()
    mentor = get_object_or_404(User, id=mentor_id)

    if request.user == mentor:
        messages.error(request, "لا يمكنك طلب الإرشاد من نفسك.")
        return redirect('mentorship:find_mentor')

    if Mentorship.objects.filter(mentor=mentor, mentee=request.user).exists():
        messages.warning(request, "لقد طلبت الإرشاد من هذا المرشد بالفعل.")
        return redirect('mentorship:find_mentor')

    Mentorship.objects.create(mentor=mentor, mentee=request.user)
    messages.success(request, f"تم إرسال طلب الإرشاد إلى {mentor.username} بنجاح!")
    return redirect('mentorship:find_mentor')


# ─────────────────────────────────────────────
# Group Views
# ─────────────────────────────────────────────

@login_required
def create_group(request):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    if request.method == 'POST':
        form = MentorshipGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            GroupChat.objects.create(group=group)
            messages.success(request, "تم إنشاء المجموعة بنجاح!")
            return redirect('mentorship:group_detail', group_id=group.id)
    else:
        form = MentorshipGroupForm()

    return render(request, 'mentorship/create_group.html', {'form': form})


@login_required
def group_detail(request, group_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    group = get_object_or_404(MentorshipGroup, id=group_id)
    user = request.user

    # انضمام تلقائي للمجموعات العامة
    if group.is_public and user not in group.members.all() and user != group.admin:
        group.members.add(user)
        messages.success(request, f"انضممت إلى مجموعة {group.name} بنجاح!")
        return redirect('mentorship:group_detail', group_id=group.id)

    # المجموعات الخاصة تتطلب طلب انضمام
    if not group.is_public and user not in group.members.all() and user != group.admin:
        messages.error(request, "يجب طلب الانضمام إلى هذه المجموعة الخاصة.")
        return redirect('mentorship:find_mentor')

    chat, _ = GroupChat.objects.get_or_create(group=group)
    messages_list = GroupMessage.objects.filter(chat=chat).order_by('sent_at')

    if request.method == 'POST':
        form = GroupMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.chat = chat
            msg.sender = user
            msg.save()
            return redirect('mentorship:group_detail', group_id=group.id)
    else:
        form = GroupMessageForm()

    return render(request, 'mentorship/group_detail.html', {
        'group': group,
        'messages': messages_list,
        'form': form,
    })


@login_required
def request_join_group(request, group_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    group = get_object_or_404(MentorshipGroup, id=group_id)
    user = request.user

    if GroupRequest.objects.filter(group=group, user=user).exists():
        messages.warning(request, "لقد أرسلت طلب انضمام لهذه المجموعة بالفعل.")
    else:
        GroupRequest.objects.create(group=group, user=user)
        messages.success(request, "تم إرسال طلب الانضمام بنجاح!")

    return redirect('mentorship:mentor_dashboard')


@login_required
def manage_group_requests(request, group_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    group = get_object_or_404(MentorshipGroup, id=group_id)
    if request.user != group.admin:
        raise PermissionDenied

    pending_requests = GroupRequest.objects.filter(group=group, status='pending')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        group_request = get_object_or_404(GroupRequest, id=request_id)

        if action == 'accept':
            group_request.status = 'accepted'
            group_request.save()
            group.members.add(group_request.user)
            messages.success(request, f"تم قبول طلب {group_request.user.username}.")
        elif action == 'reject':
            group_request.status = 'rejected'
            group_request.save()
            messages.warning(request, f"تم رفض طلب {group_request.user.username}.")

        return redirect('mentorship:manage_group_requests', group_id=group.id)

    return render(request, 'mentorship/manage_group_requests.html', {
        'group': group,
        'requests': pending_requests,
    })


@login_required
def edit_group(request, group_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    group = get_object_or_404(MentorshipGroup, id=group_id)
    if request.user != group.admin:
        raise PermissionDenied

    form = MentorshipGroupForm(instance=group)
    add_form = AddMemberForm()

    if request.method == 'POST':
        if 'update_group' in request.POST:
            form = MentorshipGroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                messages.success(request, "تم تحديث المجموعة بنجاح!")
                return redirect('mentorship:edit_group', group_id=group.id)

        elif 'add_member' in request.POST:
            add_form = AddMemberForm(request.POST)
            if add_form.is_valid():
                username = add_form.cleaned_data['username']
                User = get_user_model()
                try:
                    member = User.objects.get(username=username)
                    if member == group.admin:
                        messages.error(request, "لا يمكن إضافة المسؤول كعضو.")
                    elif member in group.members.all():
                        messages.warning(request, f"{username} عضو بالفعل في المجموعة.")
                    else:
                        group.members.add(member)
                        messages.success(request, f"تم إضافة {username} بنجاح.")
                except User.DoesNotExist:
                    messages.error(request, "المستخدم غير موجود.")
                return redirect('mentorship:edit_group', group_id=group.id)

        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            User = get_user_model()
            try:
                member = User.objects.get(id=member_id)
                if member == group.admin:
                    messages.error(request, "لا يمكن إزالة المسؤول من المجموعة.")
                else:
                    group.members.remove(member)
                    messages.success(request, f"تم إزالة {member.username} بنجاح.")
            except User.DoesNotExist:
                messages.error(request, "المستخدم غير موجود.")
            return redirect('mentorship:edit_group', group_id=group.id)

    return render(request, 'mentorship/edit_group.html', {
        'group': group,
        'form': form,
        'add_form': add_form,
    })


# ─────────────────────────────────────────────
# Rating
# ─────────────────────────────────────────────

@login_required
def rate_mentor(request, mentorship_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    mentorship = get_object_or_404(Mentorship, id=mentorship_id, mentee=request.user)

    if request.method == 'POST':
        form = MentorRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.mentorship = mentorship
            rating.mentee = request.user
            rating.save()

            # مكافأة المرشد بعملات
            try:
                coins = rating.rating * 10
                mentorship.mentor.courses_profile.add_coins(coins)
                messages.success(
                    request,
                    f"لقد قيّمت {mentorship.mentor.username} وحصلوا على {coins} عملة!"
                )
            except Exception:
                messages.success(request, f"تم إرسال تقييمك بنجاح!")

            return redirect('mentorship:mentor_dashboard')
    else:
        form = MentorRatingForm()

    return render(request, 'mentorship/rate_mentor.html', {
        'mentorship': mentorship,
        'form': form,
    })


# ─────────────────────────────────────────────
# Community Feed
# ─────────────────────────────────────────────

@login_required
def community_feed(request):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    posts = Post.objects.all().order_by('-created_at')
    user = request.user

    daily_post_count = Post.objects.filter(
        author=user,
        created_at__date=timezone.now().date()
    ).count()

    if request.method == 'POST':
        if 'post_content' in request.POST:
            content = request.POST.get('post_content', '').strip()
            image_file = request.POST.get('image_file', '').strip()
            if content or image_file:
                Post.objects.create(author=user, content=content, image_file=image_file)
                messages.success(request, "تم نشر المنشور بنجاح!")
            return redirect('mentorship:community_feed')

        elif 'comment_content' in request.POST and 'post_id' in request.POST:
            content = request.POST.get('comment_content', '').strip()
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if content:
                Comment.objects.create(post=post, author=user, content=content)
                messages.success(request, "تم إضافة التعليق بنجاح!")
            return redirect('mentorship:community_feed')

        elif 'like_post' in request.POST and 'post_id' in request.POST:
            post = get_object_or_404(Post, id=request.POST['post_id'])
            if user in post.likes.all():
                post.likes.remove(user)
            else:
                post.likes.add(user)
            return redirect('mentorship:community_feed')

        elif 'dislike_post' in request.POST and 'post_id' in request.POST:
            post = get_object_or_404(Post, id=request.POST['post_id'])
            if user in post.dislikes.all():
                post.dislikes.remove(user)
            else:
                post.dislikes.add(user)
            return redirect('mentorship:community_feed')

    return render(request, 'mentorship/community_feed.html', {
        'posts': posts,
        'daily_post_count': daily_post_count,
    })


@login_required
def post_comments(request, post_id):
    if not can_access_mentorship(request.user):
        return _deny_access(request)

    post = get_object_or_404(Post, id=post_id)
    comments = post.mentorship_comments.all().order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('comment_content', '').strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, "تم إضافة التعليق بنجاح!")
        return redirect('mentorship:post_comments', post_id=post.id)

    return render(request, 'mentorship/post_comments.html', {
        'post': post,
        'comments': comments,
    })
