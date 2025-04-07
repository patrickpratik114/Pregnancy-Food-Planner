from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserSignupForm, ProfileForm
from .models import *
from django.db import IntegrityError
from django.urls import reverse
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Meals, MealPlan
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string


# Create your views here.
def home(request):
    return render(request, 'home.html')


def get_started(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('login')


def profile(request):
    selected_day = request.GET.get('day', 'Monday')  # Default to Monday
    user_profile = get_object_or_404(Profile, user=request.user)
    meal_plan, _ = MealPlan.objects.get_or_create(user=request.user)

    # Map trimester strings to corresponding integers or values
    trimester_map = {
        'First': 1,
        'Second': 2,
        'Third': 3
    }
    trimester_value = trimester_map.get(user_profile.trimester, user_profile.trimester)

    # Filter meals strictly based on all conditions
    strict_meals = Meals.objects.filter(
        Food_Habit=user_profile.food_habits,
        Allergy=user_profile.allergy[0] if user_profile.allergy else "No Allergy",
        Genetic_Condition=user_profile.genetic_condition[0] if user_profile.genetic_condition else "No Condition",
        age=user_profile.age,
        Trimester=trimester_value
    )

    # Ensure the selected day's plan exists and is a dictionary
    if selected_day not in meal_plan.plan:
        meal_plan.plan[selected_day] = {
            'breakfast': strict_meals.filter(Meal_Type='Breakfast').order_by('?').first().Recipe if strict_meals.filter(Meal_Type='Breakfast').exists() else None,
            'lunch': strict_meals.filter(Meal_Type='Lunch').order_by('?').first().Recipe if strict_meals.filter(Meal_Type='Lunch').exists() else None,
            'dinner': strict_meals.filter(Meal_Type='Dinner').order_by('?').first().Recipe if strict_meals.filter(Meal_Type='Dinner').exists() else None
        }
        meal_plan.save()

    context = {
        'user_profile': user_profile,
        'meal_plan': meal_plan.plan.get(selected_day, {}),
        'selected_day': selected_day,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                 'Friday', 'Saturday', 'Sunday']
    }
    return render(request, 'plan.html', context)


def clear_day(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        meal_plan = get_object_or_404(MealPlan, user=request.user)
        meal_plan.clear_day(day)
        return redirect(reverse('plan') + f'?day={day}')
    return redirect('plan')



def update_meal(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        meal_type = request.POST.get('meal_type')
        user_profile = get_object_or_404(Profile, user=request.user)
        meal_plan, _ = MealPlan.objects.get_or_create(user=request.user)

        # Convert trimester to number
        trimester_map = {
            'First': 1,
            'Second': 2,
            'Third': 3
        }
        trimester_value = trimester_map.get(user_profile.trimester, user_profile.trimester)

        print("------ PROFILE DEBUG ------")
        print(f"Food Habit: {user_profile.food_habits}")
        print(f"Allergy: {user_profile.allergy}")
        print(f"Genetic Condition: {user_profile.genetic_condition}")
        print(f"Age: {user_profile.age}")
        print(f"Trimester: {trimester_value}")
        print("---------------------------")

        # Start with just Meal Type
        filtered_meals = Meals.objects.filter(Meal_Type=meal_type.capitalize())
        print(f"[DEBUG] Initially found: {filtered_meals.count()} meals for {meal_type}")

        # Apply all filters (primary logic)
        if user_profile.food_habits and user_profile.food_habits.lower() != 'any':
            filtered_meals = filtered_meals.filter(Food_Habit=user_profile.food_habits)

        if user_profile.allergy and user_profile.allergy.lower() != 'no allergy':
            filtered_meals = filtered_meals.filter(Allergy=user_profile.allergy)

        if user_profile.genetic_condition and user_profile.genetic_condition.lower() != 'no condition':
            filtered_meals = filtered_meals.filter(Genetic_Condition=user_profile.genetic_condition)

        if user_profile.age:
            filtered_meals = filtered_meals.filter(age=user_profile.age)

        if trimester_value:
            filtered_meals = filtered_meals.filter(Trimester=trimester_value)

        print(f"[DEBUG] After full filters: {filtered_meals.count()}")

       
        if not filtered_meals.exists():
            print("[DEBUG] Fallback to Meal_Type + Food_Habit")
            filtered_meals = Meals.objects.filter(
                Meal_Type=meal_type.capitalize(),
                Food_Habit=user_profile.food_habits
            )
            print(f"[DEBUG] Fallback1 meals found: {filtered_meals.count()}")

     
        if not filtered_meals.exists():
            print("[DEBUG] Fallback to Meal_Type only")
            filtered_meals = Meals.objects.filter(Meal_Type=meal_type.capitalize())
            print(f"[DEBUG] Fallback2 meals found: {filtered_meals.count()}")

        # Select and save
        if filtered_meals.exists():
            selected_meal = filtered_meals.order_by('?').first().Recipe
            print(f"[DEBUG] Selected meal: {selected_meal}")
        else:
            selected_meal = None
            print("[DEBUG] No meal found even after fallback")

        if day not in meal_plan.plan:
            meal_plan.plan[day] = {}

        meal_plan.plan[day][meal_type] = selected_meal
        meal_plan.save()

        return redirect(f'/plan/?day={day}')
    

# Email validation and verification functions
def send_verification_email(request, user):
    """
    Send verification email to user with a unique token link
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Use localhost with port for development
    domain = request.get_host() if request else "localhost:8000"
    protocol = "http"  # Use http for local development
    
    verification_url = f"{protocol}://{domain}/verify-email/{uid}/{token}/"
    
    subject = "Verify Your Email Address"
    html_message = render_to_string('email/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
    })
    plain_message = f"Hi {user.username}, please verify your email by clicking this link: {verification_url}"
    
    try:
        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email='shresthapratik124@gmail.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        print(f"Verification email result: {result}")
        print(f"Email sent to: {user.email}")
        print(f"Verification URL: {verification_url}")
        return True
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_email(request, uidb64, token):
    """
    Verify email using the token from the verification link
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Update user profile to mark email as verified
        profile = Profile.objects.get(user=user)
        profile.email_verified = True
        profile.save()
        
        messages.success(request, "Your email has been verified successfully! You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "The verification link is invalid or has expired.")
        return redirect('home')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if email is verified
            try:
                profile = Profile.objects.get(user=user)
                if not profile.email_verified:
                    messages.warning(request, "Please verify your email before logging in. Check your inbox for the verification link.")
                    # Option to resend verification email
                    if request.POST.get('resend_verification'):
                        send_verification_email(user)
                        messages.info(request, "Verification email has been resent.")
                    return render(request, 'login.html', {'resend_option': True, 'email': email})
                
                # Email verified, proceed with login
                auth_login(request, user)
                return redirect('plan')
            
            except Profile.DoesNotExist:
                messages.error(request, "User profile not found.")
                return redirect('login')
        else:
            messages.error(request, "Wrong Email or Password")
            return redirect('login')
            
    return render(request, 'login.html')


def user_logout(request):
    auth_logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        # Print all POST data for debugging
        print("POST data:", request.POST)
        
        user_form = UserSignupForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        # Print form validation status
        print("User form is valid:", user_form.is_valid())
        if not user_form.is_valid():
            print("User form errors:", user_form.errors)
        
        print("Profile form is valid:", profile_form.is_valid())
        if not profile_form.is_valid():
            print("Profile form errors:", profile_form.errors)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Try different ways of getting the email
            email = None
            if 'email' in user_form.cleaned_data:
                email = user_form.cleaned_data['email']
                print(f"Email from cleaned_data['email']: {email}")
            elif 'username' in user_form.cleaned_data:
                email = user_form.cleaned_data['username']  # If using username as email
                print(f"Email from cleaned_data['username']: {email}")
            
            # Fallbacks from POST data
            if not email:
                email = request.POST.get('email') or request.POST.get('username', '')
                print(f"Email from POST data: {email}")
            
            password = user_form.cleaned_data.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            print(f"Final email being used: '{email}'")

            # Safe check before using email
            if not email:
                messages.error(request, "Email address is required.")
                return render(request, 'signup.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                })

            # Only check domain if we have a valid email with @ symbol
            if '@' in email:
                domain = email.split('@')[1]
                if domain.lower() in ['example.com', 'test.com']:
                    messages.error(request, "Please use a real email address.")
                    return render(request, 'signup.html', {
                        'user_form': user_form,
                        'profile_form': profile_form,
                    })

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
            else:
                try:
                    # Check if email already exists
                    if User.objects.filter(email=email).exists():
                        messages.error(request, "A user with this email already exists. Please try logging in.")
                        return render(request, 'signup.html', {
                            'user_form': user_form,
                            'profile_form': profile_form,
                        })
                        
                    # Create user
                    user = user_form.save(commit=False)
                    # Make sure username is set if using email as username
                    if not user.username and email:
                        user.username = email
                    user.email = email  # Explicitly set email
                    user.set_password(password)
                    user.save()

                    # Create profile
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    
                    # Add email_verified field to profile if not exists
                    profile.email_verified = False  

                    # Convert list to comma-separated string
                    profile.allergy = ','.join(profile_form.cleaned_data.get('allergy', []) or ['No Allergy'])
                    profile.genetic_condition = ','.join(profile_form.cleaned_data.get('genetic_condition', []) or ['No Condition'])

                    profile.save()

                    # Send verification email
                    if send_verification_email(request, user):
                        messages.success(request, "Account created successfully! Please check your email to verify your account.")
                    else:
                        messages.warning(request, "Account created, but we couldn't send a verification email. Please contact support.")
                    
                    return redirect('login')

                except IntegrityError as e:
                    print(f"IntegrityError: {e}")
                    messages.error(request, f"Account creation failed: {e}")
        else:
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

def resend_verification(request):
    """View to handle resending verification emails"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if send_verification_email(user):
                messages.success(request, "Verification email sent successfully! Please check your inbox.")
            else:
                messages.error(request, "Failed to send verification email. Please try again later.")
        except User.DoesNotExist:
            messages.error(request, "No account exists with this email address.")
    
    return redirect('login')


def breakfast(request):
    return render(request, 'breakfast.html')


def lunch(request):
    return render(request, 'lunch.html')


def dinner(request):
    return render(request, 'dinner.html')


def select_meal(request):
    selected_day = request.GET.get('day', 'Monday')
    user_profile = get_object_or_404(Profile, user=request.user)
    meal_plan, _ = MealPlan.objects.get_or_create(user=request.user)

    trimester_map = {
        'First': 1,
        'Second': 2,
        'Third': 3
    }
    trimester_value = trimester_map.get(user_profile.trimester, user_profile.trimester)

    filtered_meals = Meals.objects.filter(
        Food_Habit=user_profile.food_habits,
        Allergy=user_profile.allergy[0] if user_profile.allergy else "No Allergy",
        Genetic_Condition=user_profile.genetic_condition[0] if user_profile.genetic_condition else "No Condition",
        age=user_profile.age,
        Trimester=trimester_value
    )

    if selected_day not in meal_plan.plan or not meal_plan.plan[selected_day]:
        meal_plan.plan[selected_day] = {
            'breakfast': filtered_meals.filter(Meal_Type='Breakfast').order_by('?').first().Recipe if filtered_meals.filter(Meal_Type='Breakfast').exists() else None,
            'lunch': filtered_meals.filter(Meal_Type='Lunch').order_by('?').first().Recipe if filtered_meals.filter(Meal_Type='Lunch').exists() else None,
            'dinner': filtered_meals.filter(Meal_Type='Dinner').order_by('?').first().Recipe if filtered_meals.filter(Meal_Type='Dinner').exists() else None,
        }
        meal_plan.save()

    selected_meals = meal_plan.plan[selected_day]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    return render(request, 'meal_selection.html', {
        'selected_day': selected_day,
        'selected_meals': selected_meals,
        'days': days,
    })


from django.http import JsonResponse
from .models import PregnancyDietaryNeeds

def get_nutrition_details(request):
    recipe_name = request.GET.get('recipe')

    # Use filter().first() to avoid MultipleObjectsReturned
    nutrition = PregnancyDietaryNeeds.objects.filter(recipe=recipe_name).first()

    if nutrition:
        data = {
            "calories": nutrition.calories,
            "protein": nutrition.protein,
            "vitamin_b9": nutrition.vitamin_b9,
            "vitamin_d": nutrition.vitamin_d,
            "vitamin_a": nutrition.vitamin_a,
            "iron": nutrition.iron,
            "iodine": nutrition.iodine,
            "calcium": nutrition.calcium,
            "omega_3": nutrition.omega_3,
        }
    else:
        data = {
            "error": "Nutrition data not found for recipe"
        }

    return JsonResponse(data)


from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

def custom_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                associated_users = User.objects.filter(email=email)
                
                if associated_users.exists():
                    # Get the site domain (localhost:8000)
                    site_domain = request.get_host()
                    
                    # Use Django's built-in password reset functionality
                    form.save(
                        request=request,
                        use_https=False,  # Use http for local development
                        from_email="shresthapratik124@gmail.com",
                        email_template_name='registration/password_reset_email.html',
                        subject_template_name='registration/password_reset_subject.txt',
                        domain_override=site_domain  # Important for local development
                    )
                    
                    messages.success(request, "Password reset email has been sent to your email address.")
                    return redirect('password_reset_done')
                else:
                    messages.error(request, "No user found with this email address.")
                    
            except Exception as e:
                print(f"Error in password reset: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, "Error sending password reset email. Please try again.")
    else:
        form = PasswordResetForm()
    
    return render(request, 'registration/password_reset_form.html', {'form': form})

@login_required
def update_profile(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user_profile)
        
        if profile_form.is_valid():
            try:
                profile = profile_form.save(commit=False)
                
                # Convert list to comma-separated string
                profile.allergy = ','.join(profile_form.cleaned_data.get('allergy', []) or ['No Allergy'])
                profile.genetic_condition = ','.join(profile_form.cleaned_data.get('genetic_condition', []) or ['No Condition'])
                
                profile.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('plan')
            except Exception as e:
                messages.error(request, f"Error updating profile: {e}")
    else:
        # For GET requests, pre-populate form with existing data
        # Convert comma-separated strings back to lists for the form
        initial_data = {
            'allergy': user_profile.allergy.split(',') if user_profile.allergy else ['No Allergy'],
            'genetic_condition': user_profile.genetic_condition.split(',') if user_profile.genetic_condition else ['No Condition'],
        }
        profile_form = ProfileForm(instance=user_profile, initial=initial_data)
    
    return render(request, 'update_profile.html', {
        'profile_form': profile_form,
        'user_profile': user_profile,
    })