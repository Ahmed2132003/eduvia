from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Mentorship, MentorshipGroup, GroupRequest, GroupChat, GroupMessage, MentorRating, Post, Comment
from .forms import MentorshipGroupForm, GroupMessageForm, MentorRatingForm, AddMemberForm
from courses.models import UserProfile
from accounts.models import Profile
from django.utils import timezone
import re

def clean_text(text):
    """Clean text to create a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

@login_required
def become_mentor(request):
    user = request.user
    if user.courses_profile.role == 'student':
        user.courses_profile.role = 'instructor'
        user.courses_profile.save()
        messages.success(request, "أنت الآن مرشد!")
    return redirect('mentorship:mentor_dashboard')

@login_required
def mentor_dashboard(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    subscription = profile.subscription_plan or 'free'

    mentees = Mentorship.objects.filter(mentor=user, is_active=True)
    admin_groups = MentorshipGroup.objects.filter(admin=user)
    member_groups = user.mentorship_groups.all()

    max_admin_groups = 0 if subscription == 'free' else 2 if subscription == 'basic' else 4 if subscription == 'pro' else float('inf')
    max_member_groups = 1 if subscription == 'free' else 3 if subscription == 'basic' else 6 if subscription == 'pro' else float('inf')
    current_admin = admin_groups.count()
    current_member = member_groups.exclude(admin=user).count()

    return render(request, 'mentorship/mentor_dashboard.html', {
        'mentees': mentees,
        'admin_groups': admin_groups,
        'member_groups': member_groups,
        'subscription': subscription,
        'can_create_group': current_admin < max_admin_groups if subscription != 'free' else False,
        'max_admin_groups': max_admin_groups,
        'current_admin': current_admin,
        'max_member_groups': max_member_groups,
        'current_member': current_member,
    })

@login_required
def find_mentor(request):
    User = get_user_model()
    mentors = User.objects.filter(courses_profile__role='instructor')
    public_groups = MentorshipGroup.objects.filter(is_public=True).exclude(members=request.user)
    private_groups = MentorshipGroup.objects.filter(is_public=False).exclude(members=request.user)
    
    return render(request, 'mentorship/find_mentor.html', {
        'mentors': mentors,
        'public_groups': public_groups,
        'private_groups': private_groups,
    })

@login_required
def request_mentorship(request, mentor_id):
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

@login_required
def create_group(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    subscription = profile.subscription_plan or 'free'

    if subscription == 'free':
        messages.error(request, "لا يمكنك إنشاء مجموعة في الخطة المجانية. اشترك في خطة مدفوعة.")
        return redirect('mentorship:mentor_dashboard')

    current_admin_groups = MentorshipGroup.objects.filter(admin=user).count()
    max_groups = 2 if subscription == 'basic' else 4 if subscription == 'pro' else float('inf')

    if current_admin_groups >= max_groups:
        messages.error(request, f"لقد وصلت إلى الحد الأقصى لإنشاء المجموعات ({max_groups}).")
        return redirect('mentorship:mentor_dashboard')

    if request.method == 'POST':
        form = MentorshipGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            GroupChat.objects.create(group=group)
            messages.success(request, "تم إنشاء المجموعة بنجاح!")
            return redirect('mentorship:group_detail', group_id=group.id, group_title=clean_text(group.name))
    else:
        form = MentorshipGroupForm()
    return render(request, 'mentorship/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(MentorshipGroup, id=group_id)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    subscription = profile.subscription_plan or 'free'

    if group.is_public and user not in group.members.all() and user != group.admin:
        current_member_groups = user.mentorship_groups.exclude(admin=user).count()
        max_member = 1 if subscription == 'free' else 3 if subscription == 'basic' else 6 if subscription == 'pro' else float('inf')

        if current_member_groups >= max_member:
            messages.error(request, f"You have reached the maximum limit for joining groups ({max_member}).")
            return redirect('mentorship:find_mentor')

        try:
            group.members.add(user)
            messages.success(request, f"You have successfully joined the group {group.name}!")
            return redirect('mentorship:group_detail', group_id=group.id)
        except Exception as e:
            messages.error(request, f"Failed to join: {str(e)}")
            return redirect('mentorship:find_mentor')

    if not group.is_public and user not in group.members.all() and user != group.admin:
        messages.error(request, "You must request to join this private group.")
        return redirect('mentorship:find_mentor')

    chat, created = GroupChat.objects.get_or_create(group=group)
    messages_list = GroupMessage.objects.filter(chat=chat).order_by('sent_at')

    if request.method == 'POST':
        form = GroupMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = user
            message.save()
            return redirect('mentorship:group_detail', group_id=group.id)
    else:
        form = GroupMessageForm()

    return render(request, 'mentorship/group_detail.html', {
        'group': group,
        'messages': messages_list,
        'form': form,
        'subscription': subscription,
    })

@login_required
def request_join_group(request, group_id):
    group = get_object_or_404(MentorshipGroup, id=group_id)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    subscription = profile.subscription_plan or 'free'

    current_member_groups = user.mentorship_groups.exclude(admin=user).count()
    max_member = 1 if subscription == 'free' else 3 if subscription == 'basic' else 6 if subscription == 'pro' else float('inf')

    if current_member_groups >= max_member:
        messages.error(request, f"You have reached the maximum limit for joining groups ({max_member}).")
        return redirect('mentorship:mentor_dashboard')

    if GroupRequest.objects.filter(group=group, user=user).exists():
        messages.warning(request, "You have already requested to join this group.")
    else:
        GroupRequest.objects.create(group=group, user=user)
        messages.success(request, "Group join request sent successfully!")
    return redirect('mentorship:mentor_dashboard')

@login_required
def manage_group_requests(request, group_id):
    group = get_object_or_404(MentorshipGroup, id=group_id)
    if request.user != group.admin:
        raise PermissionDenied
    requests = GroupRequest.objects.filter(group=group, status='pending')
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        group_request = get_object_or_404(GroupRequest, id=request_id)
        if action == 'accept':
            group_request.status = 'accepted'
            group_request.save()
            group.members.add(group_request.user)
            messages.success(request, f"{group_request.user.username}'s request accepted successfully.")
        elif action == 'reject':
            group_request.status = 'rejected'
            group_request.save()
            messages.warning(request, f"{group_request.user.username}'s request rejected.")
        return redirect('mentorship:manage_group_requests', group_id=group.id)
    return render(request, 'mentorship/manage_group_requests.html', {
        'group': group,
        'requests': requests,
    })

@login_required
def rate_mentor(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id, mentee=request.user)
    if request.method == 'POST':
        form = MentorRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.mentorship = mentorship
            rating.mentee = request.user
            rating.save()
            coins = rating.rating * 10
            mentorship.mentor.courses_profile.add_coins(coins)
            messages.success(request, f"لقد قيّمت {mentorship.mentor.username} وحصلوا على {coins} عملة!")
            return redirect('mentorship:mentor_dashboard')
    else:
        form = MentorRatingForm()
    return render(request, 'mentorship/rate_mentor.html', {
        'mentorship': mentorship,
        'form': form,
    })

@login_required
def community_feed(request):
    posts = Post.objects.all().order_by('-created_at')
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    subscription = profile.subscription_plan or 'free'

    # احسب عدد المنشورات اليومية للمستخدم الحالي
    daily_post_count = Post.objects.filter(
        author=user,
        created_at__date=timezone.now().date()
    ).count()

    if request.method == 'POST':
        if subscription == 'free':
            messages.error(request, "You cannot perform this action on the free plan. Upgrade to a paid plan.")
            return redirect('mentorship:community_feed')

        if 'post_content' in request.POST:
            max_posts = 4 if subscription == 'basic' else 8 if subscription == 'pro' else float('inf')

            if daily_post_count >= max_posts:
                messages.error(request, f"You have reached the maximum daily posts ({max_posts}).")
                return redirect('mentorship:community_feed')

            content = request.POST['post_content']
            image_file = request.POST.get('image_file', '')
            if content or image_file:
                post = Post.objects.create(author=user, content=content, image_file=image_file)
                messages.success(request, "Post created successfully!")
            return redirect('mentorship:community_feed')

        elif 'comment_content' in request.POST and 'post_id' in request.POST:
            content = request.POST['comment_content']
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if content:
                Comment.objects.create(post=post, author=user, content=content)
                messages.success(request, "Comment added successfully!")
            return redirect('mentorship:community_feed')

        elif 'like_post' in request.POST and 'post_id' in request.POST:
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if user in post.likes.all():
                post.likes.remove(user)
            else:
                post.likes.add(user)
            return redirect('mentorship:community_feed')

        elif 'dislike_post' in request.POST and 'post_id' in request.POST:
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if user in post.dislikes.all():
                post.dislikes.remove(user)
            else:
                post.dislikes.add(user)
            return redirect('mentorship:community_feed')

    context = {
        'posts': posts,
        'subscription': subscription,
        'daily_post_count': daily_post_count,
    }
    return render(request, 'mentorship/community_feed.html', context)

@login_required
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.mentorship_comments.all().order_by('-created_at')
    profile = get_object_or_404(Profile, user=request.user)
    subscription = profile.subscription_plan or 'free'

    return render(request, 'mentorship/post_comments.html', {
        'post': post,
        'comments': comments,
        'subscription': subscription,
    })

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(MentorshipGroup, id=group_id)
    if request.user != group.admin:
        raise PermissionDenied

    if request.method == 'POST':
        if 'update_group' in request.POST:
            form = MentorshipGroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                messages.success(request, "Group updated successfully!")
                return redirect('mentorship:edit_group', group_id=group.id)
        elif 'add_member' in request.POST:
            add_form = AddMemberForm(request.POST)
            if add_form.is_valid():
                username = add_form.cleaned_data['username']
                User = get_user_model()
                try:
                    user = User.objects.get(username=username)
                    if user == group.admin:
                        messages.error(request, "Cannot add the admin as a member.")
                    elif user in group.members.all():
                        messages.warning(request, f"{username} is already a member of the group.")
                    else:
                        group.members.add(user)
                        messages.success(request, f"{username} added to the group successfully.")
                except User.DoesNotExist:
                    messages.error(request, "User does not exist.")
                return redirect('mentorship:edit_group', group_id=group.id)
        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            User = get_user_model()
            try:
                user = User.objects.get(id=member_id)
                if user == group.admin:
                    messages.error(request, "Cannot remove the admin from the group.")
                else:
                    group.members.remove(user)
                    messages.success(request, f"{user.username} removed from the group successfully.")
                return redirect('mentorship:edit_group', group_id=group.id)
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect('mentorship:edit_group', group_id=group.id)
    else:
        form = MentorshipGroupForm(instance=group)
        add_form = AddMemberForm()

    return render(request, 'mentorship/edit_group.html', {
        'group': group,
        'form': form,
        'add_form': add_form,
    })