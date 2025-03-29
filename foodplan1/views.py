from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserSignupForm, ProfileForm
from .models import *
from django.db import IntegrityError
from django.urls import reverse
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Meals, MealPlan

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
    return render(request, 'profile.html', context)


def clear_day(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        meal_plan = get_object_or_404(MealPlan, user=request.user)
        meal_plan.clear_day(day)
        return redirect(reverse('profile') + f'?day={day}')
    return redirect('profile')


# def select_meal(request, meal_type):
#     selected_day = request.GET.get('day', 'Monday')
#     user_profile = get_object_or_404(Profile, user=request.user)
#     meal_plan, _ = MealPlan.objects.get_or_create(user=request.user)

#     # Map trimester strings to corresponding integers or values
#     trimester_map = {
#         'First': 1,
#         'Second': 2,
#         'Third': 3
#     }
#     trimester_value = trimester_map.get(user_profile.trimester, user_profile.trimester)

#     # Prepare allergy and genetic condition
#     allergy_value = user_profile.allergy[0] if user_profile.allergy else "No Allergy"
#     genetic_condition_value = user_profile.genetic_condition[0] if user_profile.genetic_condition else "No Condition"

#     # Filter meals based on user profile
#     meals = Meals.objects.filter(
#         Meal_Type=meal_type.capitalize(),
#         Food_Habit=user_profile.food_habits,
#         Allergy=allergy_value,
#         Genetic_Condition=genetic_condition_value,
#         age=user_profile.age,
#         Trimester=trimester_value
#     )

#     # If no meals match strict criteria, relax some constraints
#     if not meals.exists():
#         meals = Meals.objects.filter(
#             Meal_Type=meal_type.capitalize(),
#             Food_Habit=user_profile.food_habits
#         )

#     # Add a method to get lowercase recipe for template
#     for meal in meals:
#         meal.recipe = meal.Recipe  # Add a lowercase recipe attribute

#     context = {
#         'meals': meals,
#         'selected_day': selected_day,
#         'meal_type': meal_type
#     }

#     return render(request, 'meal_selection.html', context)


# def update_meal(request):
#     if request.method == 'POST':
#         day = request.POST.get('day')
#         meal_type = request.POST.get('meal_type')
#         recipe = request.POST.get('recipe')

#         meal_plan, _ = MealPlan.objects.get_or_create(user=request.user)
#         plan = meal_plan.plan.copy()
#         plan[day][meal_type] = recipe
#         meal_plan.plan = plan
#         meal_plan.save()

#         return redirect(reverse('profile') + f'?day={day}')

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

        return redirect(f'/profile/?day={day}')




def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
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

        if user_form.is_valid() and profile_form.is_valid():
            password = user_form.cleaned_data.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
            else:
                try:
                    user = user_form.save(commit=False)
                    user.set_password(password)
                    user.save()

                    profile = profile_form.save(commit=False)
                    profile.user = user

                    # Convert list to comma-separated string
                    profile.allergy = ','.join(profile_form.cleaned_data.get('allergy', []) or ['No Allergy'])
                    profile.genetic_condition = ','.join(profile_form.cleaned_data.get('genetic_condition', []) or ['No Condition'])

                    profile.save()

                    messages.success(request, "Account created successfully!")
                    return redirect('login')

                except IntegrityError:
                    messages.error(request, "A user with this email already exists. Please try logging in.")
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

def breakfast(request):
    return render(request, 'breakfast.html')


def lunch(request):
    return render(request, 'lunch.html')


def dinner(request):
    return render(request, 'dinner.html')



# STEP 1: Update views.py inside your `foodplan1` app

from django.shortcuts import render, get_object_or_404
from .models import Profile, Meals, MealPlan

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
