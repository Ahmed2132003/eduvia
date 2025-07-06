from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mentorship, MentorshipGroup, GroupRequest, GroupChat, GroupMessage, MentorRating, Post, Comment
from .forms import MentorshipGroupForm, GroupMessageForm, MentorRatingForm
from django.core.exceptions import PermissionDenied
from courses.models import UserProfile
from django.conf import settings
from django.contrib.auth import get_user_model

@login_required
def become_mentor(request):
    user = request.user
    if user.courses_profile.role == 'student':
        user.courses_profile.role = 'instructor'
        user.courses_profile.save()
        messages.success(request, "You are now a mentor!")
    return redirect('mentorship:mentor_dashboard')

@login_required
def mentor_dashboard(request):
    user = request.user
    mentees = Mentorship.objects.filter(mentor=user, is_active=True)
    admin_groups = MentorshipGroup.objects.filter(admin=user)
    member_groups = user.mentorship_groups.all()
    return render(request, 'mentorship/mentor_dashboard.html', {
        'mentees': mentees,
        'admin_groups': admin_groups,
        'member_groups': member_groups,
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
        messages.error(request, "You cannot request mentorship from yourself.")
        return redirect('mentorship:find_mentor')
    
    if Mentorship.objects.filter(mentor=mentor, mentee=request.user).exists():
        messages.warning(request, "You have already requested mentorship from this mentor.")
        return redirect('mentorship:find_mentor')
    
    Mentorship.objects.create(mentor=mentor, mentee=request.user)
    messages.success(request, f"Mentorship request sent to {mentor.username} successfully!")
    return redirect('mentorship:find_mentor')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = MentorshipGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            GroupChat.objects.create(group=group)
            messages.success(request, "Group created successfully!")
            return redirect('mentorship:group_detail', group_id=group.id)
    else:
        form = MentorshipGroupForm()
    return render(request, 'mentorship/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(MentorshipGroup, id=group_id)
    
    if group.is_public and request.user not in group.members.all() and request.user != group.admin:
        try:
            group.members.add(request.user)
            messages.success(request, f"You have successfully joined the group {group.name}!")
            return redirect('mentorship:group_detail', group_id=group.id)
        except Exception as e:
            messages.error(request, f"Failed to join the group: {str(e)}")
            return redirect('mentorship:find_mentor')
    
    if not group.is_public and request.user not in group.members.all() and request.user != group.admin:
        messages.error(request, "You need to request to join this private group.")
        return redirect('mentorship:find_mentor')
    
    chat, created = GroupChat.objects.get_or_create(group=group)
    messages_list = GroupMessage.objects.filter(chat=chat).order_by('sent_at')
    
    if request.method == 'POST':
        form = GroupMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
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
    group = get_object_or_404(MentorshipGroup, id=group_id)
    if GroupRequest.objects.filter(group=group, user=request.user).exists():
        messages.warning(request, "You already requested to join this group.")
    else:
        GroupRequest.objects.create(group=group, user=request.user)
        messages.success(request, "Your request to join the group has been sent!")
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
            messages.success(request, f"{group_request.user.username}'s request has been accepted.")
        elif action == 'reject':
            group_request.status = 'rejected'
            group_request.save()
            messages.warning(request, f"{group_request.user.username}'s request has been rejected.")
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
            messages.success(request, f"You rated {mentorship.mentor.username} and they earned {coins} coins!")
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
    if request.method == 'POST':
        if 'post_content' in request.POST:
            content = request.POST['post_content']
            image_file = request.POST.get('image_file', '')  
            if content or image_file:
                post = Post.objects.create(author=request.user, content=content, image_file=image_file)
                messages.success(request, "Post created successfully!")
            return redirect('mentorship:community_feed')
        elif 'comment_content' in request.POST and 'post_id' in request.POST:
            content = request.POST['comment_content']
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if content:
                Comment.objects.create(post=post, author=request.user, content=content)
                messages.success(request, "Comment added successfully!")
            return redirect('mentorship:community_feed')
        elif 'like_post' in request.POST and 'post_id' in request.POST:
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
            return redirect('mentorship:community_feed')
        elif 'dislike_post' in request.POST and 'post_id' in request.POST:
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            if request.user in post.dislikes.all():
                post.dislikes.remove(request.user)
            else:
                post.dislikes.add(request.user)
            return redirect('mentorship:community_feed')
    return render(request, 'mentorship/community_feed.html', {'posts': posts})

@login_required
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.mentorship_comments.all().order_by('-created_at')
    return render(request, 'mentorship/post_comments.html', {'post': post, 'comments': comments})


from django import forms
from django.contrib.auth.models import User

class AddMemberForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")

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
                try:
                    user = User.objects.get(username=username)
                    if user == group.admin:
                        messages.error(request, "You cannot add the admin as a member.")
                    elif user in group.members.all():
                        messages.warning(request, f"{username} is already a member of the group.")
                    else:
                        group.members.add(user)
                        messages.success(request, f"{username} has been added to the group.")
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
                return redirect('mentorship:edit_group', group_id=group.id)
        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                user = User.objects.get(id=member_id)
                if user == group.admin:
                    messages.error(request, "You cannot remove the admin from the group.")
                else:
                    group.members.remove(user)
                    messages.success(request, f"{user.username} has been removed from the group.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            return redirect('mentorship:edit_group', group_id=group.id)
    else:
        form = MentorshipGroupForm(instance=group)
        add_form = AddMemberForm()
    
    return render(request, 'mentorship/edit_group.html', {
        'group': group,
        'form': form,
        'add_form': add_form,
    })