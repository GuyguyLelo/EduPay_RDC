"""
URLs pour l'app core
"""
from django.urls import path
from . import views, views_templates

app_name = 'core'

urlpatterns = [
    # API endpoints
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/profile/', views.profile, name='api_profile'),
    path('api/users/', views.list_users, name='api_list_users'),
    
    # Template views
    path('register/', views_templates.register_view, name='register'),
    path('login/', views_templates.login_view, name='login'),
    path('logout/', views_templates.logout_view, name='logout'),
    path('profile/', views_templates.profile_view, name='profile'),
    path('change-password/', views_templates.change_password_view, name='change_password'),
    path('dashboard/', views_templates.dashboard_view, name='dashboard'),
]

