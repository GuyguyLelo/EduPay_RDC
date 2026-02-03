"""
URLs pour l'app frais
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'frais', views.FraisViewSet, basename='frais')

app_name = 'frais'

urlpatterns = [
    path('', include(router.urls)),
]

