from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserSignupForm, ProfileForm
from .models import *
from django.db import IntegrityError
# Create your views here.
def home(request):
    return render(request,'home.html')


def get_started(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('login')
    
    
def profile(request):
    return render(request, 'profile.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password = password)
        if user is not None:
            auth_login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Wrong Email or Password")
            return redirect('user_login')
    return render(request, 'login.html')


def user_logout(request):
    auth_logout(request)
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST)
        profile_form = ProfileForm(request.POST)

        # Check if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            password = user_form.cleaned_data.get('password')
            confirm_password = request.POST.get('confirm_password')  # Validate against POST data

            # Check if passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
            else:
                try:
                    # Save User
                    user = user_form.save(commit=False)
                    user.set_password(password)
                    user.save()

                    # Save Profile
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()

                    messages.success(request, "Account created successfully!")
                    return redirect('login')  # Replace 'login' with your login URL name

                except IntegrityError:
                    messages.error(request, "A user with this email already exists. Please try logging in.")
        else:
            # Add specific error messages based on form errors
            for field, error in user_form.errors.items():
                messages.error(request, f"{field.capitalize()}: {', '.join(error)}")
            for field, error in profile_form.errors.items():
                messages.error(request, f"{field.capitalize()}: {', '.join(error)}")
    else:
        user_form = UserSignupForm()
        profile_form = ProfileForm()

    return render(request, 'signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
    
    
    
def breakfast(request):
    return render(request, 'breakfast.html')


def lunch(request):
    return render(request, 'lunch.html')


def dinner(request):
    return render(request, 'dinner.html')