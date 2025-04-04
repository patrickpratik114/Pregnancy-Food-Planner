from django.urls import path
from . import views
from .views import (
    select_meal, update_meal, clear_day, get_nutrition_details
)

urlpatterns = [
    path('', views.home, name='home'),
    path('get_started', views.get_started, name='starter'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('select_meal/', select_meal, name='select_meal'),
    path('update_meal/', update_meal, name='update_meal'),
    path('nutrition-details/', get_nutrition_details, name='nutrition_details'),
    path('clear_day/', clear_day, name='clear_day'),

]
