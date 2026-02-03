"""
Admin configuration pour les modèles d'abonnements
"""
from django.contrib import admin
from .models import Abonnement, Facture


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    """Configuration admin pour Abonnement"""
    list_display = (
        'etablissement', 'type', 'statut', 'montant_mensuel',
        'date_debut', 'date_fin', 'limite_etudiants', 'limite_transactions_mois'
    )
    list_filter = ('type', 'statut', 'date_debut', 'date_fin')
    search_fields = ('etablissement__nom',)
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        ('Informations générales', {
            'fields': ('etablissement', 'type', 'statut')
        }),
        ('Période et montant', {
            'fields': ('montant_mensuel', 'date_debut', 'date_fin')
        }),
        ('Limites', {
            'fields': ('limite_etudiants', 'limite_transactions_mois')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """Configuration admin pour Facture"""
    list_display = (
        'numero_facture', 'abonnement', 'montant', 'devise',
        'date_emission', 'date_echeance', 'payee', 'date_paiement'
    )
    list_filter = ('payee', 'date_emission', 'date_echeance')
    search_fields = ('numero_facture', 'abonnement__etablissement__nom')
    readonly_fields = ('date_emission',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('abonnement', 'numero_facture', 'montant', 'devise')
        }),
        ('Paiement', {
            'fields': ('payee', 'date_emission', 'date_echeance', 'date_paiement')
        }),
    )
