"""
URLs templates pour les établissements
"""
from django.urls import path
from . import views_templates

app_name = 'etablissements_templates'

urlpatterns = [
    path('dashboard/', views_templates.dashboard_etablissement, name='etablissement_dashboard'),
    path('etudiants/', views_templates.etudiants_list, name='etablissement_etudiants'),
    path('etudiants/<int:etudiant_id>/', views_templates.etudiant_detail, name='etudiant_detail'),
    path('etudiants/<int:etudiant_id>/edit/', views_templates.etudiant_edit, name='etudiant_edit'),
    path('paiements/', views_templates.paiements_list, name='etablissement_paiements'),
    path('paiements/<int:paiement_id>/', views_templates.paiement_detail, name='paiement_detail'),
    path('comptes/', views_templates.comptes_paiement_list, name='etablissement_comptes'),
    path('comptes/<int:compte_id>/', views_templates.compte_detail, name='compte_detail'),
    path('comptes/<int:compte_id>/edit/', views_templates.compte_edit, name='compte_edit'),
]

