"""
URLs pour l'app etudiants
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'etudiants', views.EtudiantViewSet, basename='etudiant')

app_name = 'etudiants'

urlpatterns = [
    path('', include(router.urls)),
]

