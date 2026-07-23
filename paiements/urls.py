"""
URLs pour l'app paiements
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_templates

router = DefaultRouter()
router.register(r'paiements', views.PaiementViewSet, basename='paiement')

app_name = 'paiements'

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/cinetpay/', views.webhook_cinetpay, name='webhook_cinetpay'),
    path('webhook/flutterwave/', views.webhook_flutterwave, name='webhook_flutterwave'),
    # URLs templates pour les paiements
    path('liste/', views_templates.liste_paiements, name='liste_paiements'),
    path('payer/<int:frais_id>/', views_templates.payer_frais, name='paiement_create'),
    path('selection/<int:paiement_id>/', views_templates.selection_mode_paiement, name='selection_mode_paiement'),
    path('traiter/<int:paiement_id>/', views_templates.traiter_mode_paiement, name='traiter_mode_paiement'),
    path('verifier/<int:paiement_id>/', views_templates.paiement_verifier, name='paiement_verifier'),
    path('receipt/<int:paiement_id>/', views_templates.paiement_receipt, name='paiement_receipt'),
    path('success/<int:paiement_id>/', views_templates.paiement_success, name='paiement_success'),
]

