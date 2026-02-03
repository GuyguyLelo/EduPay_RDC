"""
URLs templates pour les paiements
"""
from django.urls import path
from . import views_templates

app_name = 'paiements_templates'

urlpatterns = [
    path('payer/<int:frais_id>/', views_templates.payer_frais, name='paiement_create'),
    path('success/<int:paiement_id>/', views_templates.paiement_success, name='paiement_success'),
    path('cancel/<int:paiement_id>/', views_templates.paiement_cancel, name='paiement_cancel'),
    path('qr-code/<int:paiement_id>/', views_templates.paiement_qr_code, name='paiement_qr_code'),
    path('verifier/<int:paiement_id>/', views_templates.paiement_verifier, name='paiement_verifier'),
    path('receipt/<int:paiement_id>/', views_templates.paiement_receipt, name='paiement_receipt'),
]

