"""
URLs pour le dashboard admin
"""
from django.urls import path
from . import views, views_templates

app_name = 'dashboard_admin'

urlpatterns = [
    # API endpoints
    path('api/overview/', views.dashboard_overview, name='api_overview'),
    path('api/etablissements/', views.etablissements_list, name='api_etablissements_list'),
    path('api/etablissements/<int:etablissement_id>/activer/', views.activer_etablissement, name='api_activer_etablissement'),
    path('api/etablissements/<int:etablissement_id>/suspendre/', views.suspendre_etablissement, name='api_suspendre_etablissement'),
    path('api/paiements/', views.paiements_list, name='api_paiements_list'),
    path('api/rapports/mensuels/', views.rapports_mensuels, name='api_rapports_mensuels'),
    path('api/abonnements/', views.abonnements_list, name='api_abonnements_list'),
    
    # Template views
    path('', views_templates.dashboard_overview, name='dashboard_overview'),
    path('etablissements/', views_templates.etablissements_list, name='dashboard_etablissements'),
    path('paiements/', views_templates.paiements_list, name='dashboard_paiements'),
    path('rapports/', views_templates.rapports_view, name='dashboard_rapports'),
    path('abonnements/', views_templates.abonnements_list, name='dashboard_abonnements'),
    
    # Actions sur les établissements (pour les templates)
    path('etablissements/<int:etablissement_id>/activer/', views_templates.activer_etablissement_view, name='api_activer_etablissement'),
    path('etablissements/<int:etablissement_id>/suspendre/', views_templates.suspendre_etablissement_view, name='api_suspendre_etablissement'),
    path('etablissements/<int:etablissement_id>/', views_templates.etablissement_detail, name='etablissement_detail'),
    path('etablissements/<int:etablissement_id>/edit/', views_templates.etablissement_edit, name='etablissement_edit'),
    path('paiements/<int:paiement_id>/', views_templates.paiement_detail, name='paiement_detail'),
    path('abonnements/<int:abonnement_id>/', views_templates.abonnement_detail, name='abonnement_detail'),
    path('abonnements/<int:abonnement_id>/edit/', views_templates.abonnement_edit, name='abonnement_edit'),
]

