from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse

def instructor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in.')
            return redirect('login')
        if request.user.courses_profile.role != 'instructor':
            messages.error(request, 'You are not authorized to access the instructor dashboard.')
            return redirect('courses:courses')
        return view_func(request, *args, **kwargs)
    return wrapper