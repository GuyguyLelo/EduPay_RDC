"""
URLs pour l'app etablissements
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'etablissements', views.EtablissementViewSet, basename='etablissement')
router.register(r'comptes-paiement', views.ComptePaiementViewSet, basename='compte-paiement')

app_name = 'etablissements'

urlpatterns = [
    path('', include(router.urls)),
]

