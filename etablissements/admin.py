"""
Admin configuration pour les modèles d'établissements
"""
from django.contrib import admin
from .models import Etablissement, ComptePaiement, TypeEtablissement, StatutEtablissement


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    """Configuration admin pour Etablissement"""
    list_display = ('nom', 'type', 'email', 'telephone', 'statut', 'date_inscription')
    list_filter = ('type', 'statut', 'date_inscription')
    search_fields = ('nom', 'email', 'telephone')
    readonly_fields = ('date_inscription',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'type', 'email', 'telephone', 'adresse', 'logo')
        }),
        ('Statut et administration', {
            'fields': ('statut', 'admin', 'date_inscription')
        }),
    )


@admin.register(ComptePaiement)
class ComptePaiementAdmin(admin.ModelAdmin):
    """Configuration admin pour ComptePaiement"""
    list_display = ('etablissement', 'intitule', 'operateur', 'numero_compte', 'actif', 'date_creation')
    list_filter = ('operateur', 'actif', 'date_creation')
    search_fields = ('etablissement__nom', 'intitule', 'numero_compte')
    readonly_fields = ('date_creation',)
