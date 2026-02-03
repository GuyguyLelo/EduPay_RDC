"""
Admin configuration pour les modèles de paiements
"""
from django.contrib import admin
from .models import Paiement, StatutPaiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """Configuration admin pour Paiement"""
    list_display = (
        'id', 'etudiant', 'frais', 'montant', 'devise', 'statut',
        'commission_plateforme', 'date_paiement', 'date_creation'
    )
    list_filter = ('statut', 'devise', 'date_creation', 'date_paiement')
    search_fields = (
        'etudiant__nom', 'etudiant__prenom', 'etudiant__matricule',
        'reference_flutterwave', 'transaction_id'
    )
    readonly_fields = ('date_creation', 'date_modification', 'commission_plateforme')
    fieldsets = (
        ('Informations de base', {
            'fields': ('etudiant', 'frais', 'montant', 'devise')
        }),
        ('Statut et références', {
            'fields': (
                'statut', 'reference_flutterwave', 'transaction_id',
                'date_paiement', 'message_erreur'
            ),
            'description': 'Référence de paiement (CinetPay)'
        }),
        ('Commission', {
            'fields': ('taux_commission', 'commission_plateforme')
        }),
        ('Informations Mobile Money', {
            'fields': ('numero_telephone', 'operateur')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Rend certains champs en lecture seule après création"""
        readonly = list(self.readonly_fields)
        if obj:  # Si l'objet existe déjà
            readonly.extend(['etudiant', 'frais', 'montant', 'devise'])
        return readonly
