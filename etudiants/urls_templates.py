"""
URLs templates pour les étudiants
"""
from django.urls import path
from . import views_templates

app_name = 'etudiants_templates'

urlpatterns = [
    path('dashboard/', views_templates.dashboard_etudiant, name='etudiant_dashboard'),
]

