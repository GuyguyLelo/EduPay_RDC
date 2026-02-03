"""
URLs templates pour les frais
"""
from django.urls import path
from . import views_templates

app_name = 'frais_templates'

urlpatterns = [
    path('', views_templates.frais_list, name='frais_list'),
    path('<int:frais_id>/', views_templates.frais_detail, name='frais_detail'),
    path('<int:frais_id>/edit/', views_templates.frais_edit, name='frais_edit'),
]

