"""
Modèles pour la gestion des étudiants
"""
from django.db import models
from django.conf import settings
from etablissements.models import Etablissement


class Etudiant(models.Model):
    """
    Modèle représentant un étudiant/élève
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='etudiant',
        verbose_name='Utilisateur'
    )
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    matricule = models.CharField(max_length=50, unique=True, verbose_name='Matricule')
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='etudiants',
        verbose_name='Établissement'
    )
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'inscription')
    telephone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Téléphone'
    )
    
    class Meta:
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'
        ordering = ['nom', 'prenom']
        unique_together = ['matricule', 'etablissement']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"
    
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'étudiant"""
        return f"{self.nom} {self.prenom}"
