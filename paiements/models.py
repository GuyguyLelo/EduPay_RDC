"""
Modèles pour la gestion des paiements
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from etudiants.models import Etudiant
from frais.models import Frais, Devise
from etablissements.models import OperateurMobileMoney


class StatutPaiement(models.TextChoices):
    """Statuts des paiements"""
    PENDING = 'PENDING', 'En attente'
    SUCCESS = 'SUCCESS', 'Réussi'
    FAILED = 'FAILED', 'Échoué'
    CANCELLED = 'CANCELLED', 'Annulé'


class MethodePaiement(models.TextChoices):
    """Méthodes de paiement disponibles"""
    MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'
    CARTE_BANCAIRE = 'CARTE_BANCAIRE', 'Carte Bancaire'
    QR_CODE = 'QR_CODE', 'QR Code'


class Paiement(models.Model):
    """
    Modèle représentant un paiement de frais scolaire
    """
    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name='Étudiant'
    )
    frais = models.ForeignKey(
        Frais,
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name='Frais'
    )
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
    statut = models.CharField(
        max_length=20,
        choices=StatutPaiement.choices,
        default=StatutPaiement.PENDING,
        verbose_name='Statut'
    )
    reference_flutterwave = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Référence de paiement'
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ID Transaction'
    )
    commission_plateforme = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Commission plateforme'
    )
    taux_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2.0'),
        verbose_name='Taux de commission (%)'
    )
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name='Date de paiement')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    message_erreur = models.TextField(null=True, blank=True, verbose_name='Message d\'erreur')
    
    # Méthode de paiement
    methode_paiement = models.CharField(
        max_length=20,
        choices=MethodePaiement.choices,
        default=MethodePaiement.MOBILE_MONEY,
        verbose_name='Méthode de paiement'
    )
    
    # Informations de paiement Mobile Money
    numero_telephone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Numéro de téléphone'
    )
    operateur = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=OperateurMobileMoney.choices,
        verbose_name='Opérateur Mobile Money'
    )
    
    # Informations de paiement par carte bancaire
    email_paiement = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email pour le paiement'
    )
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['statut', 'date_creation']),
            models.Index(fields=['reference_flutterwave']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"Paiement {self.id} - {self.etudiant.nom_complet} - {self.montant} {self.devise}"
    
    def calculer_commission(self):
        """Calcule la commission de la plateforme"""
        from decimal import Decimal
        # S'assurer que taux_commission est un Decimal
        taux = Decimal(str(self.taux_commission))
        self.commission_plateforme = (self.montant * taux) / Decimal('100')
        return self.commission_plateforme
    
    def save(self, *args, **kwargs):
        """Surcharge pour calculer automatiquement la commission"""
        if not self.commission_plateforme or self.commission_plateforme == 0:
            self.calculer_commission()
        super().save(*args, **kwargs)
    
    @property
    def montant_etablissement(self):
        """Montant qui revient à l'établissement (après commission)"""
        return self.montant - self.commission_plateforme
    
    @property
    def is_success(self):
        """Vérifie si le paiement a réussi"""
        return self.statut == StatutPaiement.SUCCESS
    
    @property
    def is_pending(self):
        """Vérifie si le paiement est en attente"""
        return self.statut == StatutPaiement.PENDING
    
    def get_operateur_display(self):
        """Retourne le nom d'affichage de l'opérateur"""
        if not self.operateur:
            return None
        
        # Utiliser get_FOO_display() si le champ a des choices
        try:
            return super().get_operateur_display()
        except (AttributeError, ValueError):
            # Fallback si la valeur n'est pas dans les choices
            operateur_mapping = {
                'MPESA': 'M-Pesa',
                'ORANGE': 'Orange Money',
                'AIRTEL': 'Airtel Money',
                'MTN': 'MTN Mobile Money',
                'MOOV': 'Moov Money'
            }
            return operateur_mapping.get(self.operateur.upper(), self.operateur)