"""
URLs pour l'app paiements
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'paiements', views.PaiementViewSet, basename='paiement')

app_name = 'paiements'

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/cinetpay/', views.webhook_cinetpay, name='webhook_cinetpay'),
]

