"""
URLs pour l'app frais
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_templates

router = DefaultRouter()
router.register(r'frais', views.FraisViewSet, basename='frais')

app_name = 'frais'

urlpatterns = [
    path('', include(router.urls)),
    # URLs templates pour les frais
    path('liste/', views_templates.frais_list, name='liste_frais'),
]

