from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserCreationForm, ProfileForm, UserUpdateForm
from .models import Profile
import json
from django.http import JsonResponse

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            # Save the user first
            user = form.save()
            
            # Create and save the profile
            profile = Profile.objects.create(
                user=user,
                phone=profile_form.cleaned_data.get('phone'),
                registration_number=profile_form.cleaned_data.get('registration_number'),
                course=profile_form.cleaned_data.get('course'),
                year_of_study=profile_form.cleaned_data.get('year_of_study')
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
        profile_form = ProfileForm()
    
    return render(request, 'users/register.html', {
        'form': form,
        'profile_form': profile_form
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully',
                    'data': {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'course': profile.course,
                        'year_of_study': profile.year_of_study,
                        'phone': profile.phone,
                        'registration_number': profile.registration_number,
                    }
                })
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Form validation failed',
                    'errors': {
                        'user_form': user_form.errors,
                        'profile_form': profile_form.errors,
                    }
                })
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    total_bookings = request.user.booking_set.count()
    active_bookings = request.user.booking_set.filter(status='confirmed').count()
    recent_bookings = request.user.booking_set.order_by('-created_at')[:5]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home')

