"""
URLs administratives temporaires pour Render
"""
from django.urls import path
from . import views_admin

app_name = 'admin_setup'

urlpatterns = [
    # Configuration rapide
    path('quick-setup/', views_admin.quick_setup_view, name='quick_setup'),
    
    # Création manuelle du superutilisateur
    path('create-superuser/', views_admin.create_superuser_view, name='create_superuser'),
    
    # Configuration de l'établissement
    path('setup-etablissement/', views_admin.setup_etablissement_view, name='setup_etablissement'),
]
