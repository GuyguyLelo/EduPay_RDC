"""
Modèles pour la gestion des établissements scolaires
"""
from django.db import models
from django.core.validators import RegexValidator
from core.models import User


class TypeEtablissement(models.TextChoices):
    """Types d'établissements"""
    ECOLE = 'ECOLE', 'École'
    INSTITUT = 'INSTITUT', 'Institut Supérieur'
    UNIVERSITE = 'UNIVERSITE', 'Université'


class StatutEtablissement(models.TextChoices):
    """Statuts des établissements"""
    ACTIF = 'ACTIF', 'Actif'
    SUSPENDU = 'SUSPENDU', 'Suspendu'
    EN_ATTENTE = 'EN_ATTENTE', 'En attente de validation'


class Etablissement(models.Model):
    """
    Modèle représentant un établissement scolaire
    """
    nom = models.CharField(max_length=200, verbose_name='Nom de l\'établissement')
    type = models.CharField(
        max_length=20,
        choices=TypeEtablissement.choices,
        verbose_name='Type d\'établissement'
    )
    email = models.EmailField(verbose_name='Email')
    telephone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format de téléphone invalide")],
        verbose_name='Téléphone'
    )
    adresse = models.TextField(verbose_name='Adresse complète')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name='Logo')
    statut = models.CharField(
        max_length=20,
        choices=StatutEtablissement.choices,
        default=StatutEtablissement.EN_ATTENTE,
        verbose_name='Statut'
    )
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'inscription')
    admin = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etablissement_admin',
        verbose_name='Administrateur'
    )
    
    class Meta:
        verbose_name = 'Établissement'
        verbose_name_plural = 'Établissements'
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"
    
    @property
    def is_actif(self):
        """Vérifie si l'établissement est actif"""
        return self.statut == StatutEtablissement.ACTIF


class OperateurMobileMoney(models.TextChoices):
    """Opérateurs Mobile Money disponibles en RDC"""
    MPESA = 'MPESA', 'M-Pesa'
    ORANGE = 'ORANGE', 'Orange Money'
    AIRTEL = 'AIRTEL', 'Airtel Money'
    MTN = 'MTN', 'MTN Mobile Money'
    MOOV = 'MOOV', 'Moov Money'


class ComptePaiement(models.Model):
    """
    Comptes Mobile Money configurés pour chaque établissement
    """
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='comptes_paiement',
        verbose_name='Établissement'
    )
    intitule = models.CharField(
        max_length=100,
        verbose_name='Intitulé du compte',
        help_text='Ex: Compte principal, Compte Orange Money, etc.',
        default=''
    )
    operateur = models.CharField(
        max_length=20,
        choices=OperateurMobileMoney.choices,
        verbose_name='Opérateur'
    )
    numero_compte = models.CharField(max_length=50, verbose_name='Numéro de compte')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    
    class Meta:
        verbose_name = 'Compte de paiement'
        verbose_name_plural = 'Comptes de paiement'
        unique_together = ['etablissement', 'operateur']
    
    def __str__(self):
        if self.intitule:
            return f"{self.etablissement.nom} - {self.intitule} ({self.get_operateur_display()})"
        return f"{self.etablissement.nom} - {self.get_operateur_display()} ({self.numero_compte})"
