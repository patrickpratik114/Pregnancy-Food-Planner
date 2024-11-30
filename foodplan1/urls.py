from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_started', views.get_started, name='starter'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
