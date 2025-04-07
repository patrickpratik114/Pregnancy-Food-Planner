from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    select_meal, update_meal, clear_day, get_nutrition_details
)

urlpatterns = [
    path('', views.home, name='home'),
    path('get_started', views.get_started, name='starter'),
    path('plan/', views.profile, name='plan'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('select_meal/', select_meal, name='select_meal'),
    path('update_meal/', update_meal, name='update_meal'),
    path('nutrition-details/', get_nutrition_details, name='nutrition_details'),
    path('clear_day/', clear_day, name='clear_day'),
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', 
        auth_views.PasswordResetDoneView.as_view(), 
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            success_url='/reset/done/'
        ), 
        name='password_reset_confirm'),
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
    path('profile/', views.update_profile, name='profile'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]