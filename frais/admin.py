"""
Admin configuration pour les modèles de frais
"""
from django.contrib import admin
from .models import Frais


@admin.register(Frais)
class FraisAdmin(admin.ModelAdmin):
    """Configuration admin pour Frais"""
    list_display = ('nom_frais', 'etablissement', 'montant', 'devise', 'annee_academique', 'actif', 'date_creation')
    list_filter = ('devise', 'actif', 'annee_academique', 'date_creation')
    search_fields = ('nom_frais', 'etablissement__nom', 'description')
    readonly_fields = ('date_creation',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('etablissement', 'nom_frais', 'description')
        }),
        ('Montant et période', {
            'fields': ('montant', 'devise', 'annee_academique', 'actif', 'date_creation')
        }),
    )
