"""
URLs pour l'app etudiants
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_templates

router = DefaultRouter()
router.register(r'etudiants', views.EtudiantViewSet, basename='etudiant')

app_name = 'etudiants'

urlpatterns = [
    path('', include(router.urls)),
    # URLs templates pour les étudiants
    path('dashboard/', views_templates.dashboard_etudiant, name='etudiant_dashboard'),
    path('mes-frais/', views_templates.mes_frais, name='mes_frais'),
    path('mes-paiements/', views_templates.mes_paiements, name='mes_paiements'),
    path('mes-recus/', views_templates.mes_recus, name='mes_recus'),
]

