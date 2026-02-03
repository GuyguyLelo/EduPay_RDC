"""
Modèles pour la gestion des frais scolaires
"""
from django.db import models
from django.core.validators import MinValueValidator
from etablissements.models import Etablissement


class Devise(models.TextChoices):
    """Devises acceptées"""
    CDF = 'CDF', 'Franc Congolais (CDF)'
    USD = 'USD', 'Dollar Américain (USD)'


class Frais(models.Model):
    """
    Modèle représentant un type de frais scolaire
    """
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='frais',
        verbose_name='Établissement'
    )
    nom_frais = models.CharField(max_length=200, verbose_name='Nom des frais')
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant'
    )
    devise = models.CharField(
        max_length=3,
        choices=Devise.choices,
        default=Devise.CDF,
        verbose_name='Devise'
    )
    annee_academique = models.CharField(max_length=20, verbose_name='Année académique')
    description = models.TextField(null=True, blank=True, verbose_name='Description')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    
    class Meta:
        verbose_name = 'Frais'
        verbose_name_plural = 'Frais'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom_frais} - {self.etablissement.nom} ({self.montant} {self.devise})"
