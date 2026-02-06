"""
URLs administratives temporaires pour Render
"""
from django.urls import path
from . import views_admin

app_name = 'admin_setup'

urlpatterns = [
    # Création du superutilisateur principal
    path('create-master-superuser/', views_admin.create_master_superuser_view, name='create_master_superuser'),
    
    # Configuration rapide
    path('quick-setup/', views_admin.quick_setup_view, name='quick_setup'),
    
    # Création manuelle du superutilisateur
    path('create-superuser/', views_admin.create_superuser_view, name='create_superuser'),
    
    # Configuration de l'établissement
    path('setup-etablissement/', views_admin.setup_etablissement_view, name='setup_etablissement'),
    
    # Débogage
    path('debug-users/', views_admin.debug_users_view, name='debug_users'),
    
    # Connexion forcée
    path('force-login/', views_admin.force_login_view, name='force_login'),
]
