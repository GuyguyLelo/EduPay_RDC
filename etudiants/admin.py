"""
Admin configuration pour les modèles d'étudiants
"""
from django.contrib import admin
from .models import Etudiant


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    """Configuration admin pour Etudiant"""
    list_display = ('nom', 'prenom', 'matricule', 'etablissement', 'date_inscription')
    list_filter = ('etablissement', 'date_inscription')
    search_fields = ('nom', 'prenom', 'matricule', 'user__email')
    readonly_fields = ('date_inscription',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'nom', 'prenom', 'matricule', 'telephone')
        }),
        ('Établissement', {
            'fields': ('etablissement', 'date_inscription')
        }),
    )
