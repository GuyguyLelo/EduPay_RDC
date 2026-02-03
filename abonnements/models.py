"""
Modèles pour la gestion des abonnements des établissements
"""
from django.db import models
from django.core.validators import MinValueValidator
from etablissements.models import Etablissement


class TypeAbonnement(models.TextChoices):
    """Types d'abonnements disponibles"""
    GRATUIT = 'GRATUIT', 'Gratuit (Essai)'
    BASIQUE = 'BASIQUE', 'Basique'
    PREMIUM = 'PREMIUM', 'Premium'
    ENTERPRISE = 'ENTERPRISE', 'Entreprise'


class StatutAbonnement(models.TextChoices):
    """Statuts des abonnements"""
    ACTIF = 'ACTIF', 'Actif'
    EXPIRE = 'EXPIRE', 'Expiré'
    SUSPENDU = 'SUSPENDU', 'Suspendu'
    ANNULE = 'ANNULE', 'Annulé'


class Abonnement(models.Model):
    """
    Modèle représentant un abonnement d'établissement
    """
    etablissement = models.OneToOneField(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='abonnement',
        verbose_name='Établissement'
    )
    type = models.CharField(
        max_length=20,
        choices=TypeAbonnement.choices,
        default=TypeAbonnement.GRATUIT,
        verbose_name='Type d\'abonnement'
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutAbonnement.choices,
        default=StatutAbonnement.ACTIF,
        verbose_name='Statut'
    )
    montant_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Montant mensuel'
    )
    date_debut = models.DateField(verbose_name='Date de début')
    date_fin = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    
    # Limites selon le type d'abonnement
    limite_etudiants = models.IntegerField(
        default=100,
        verbose_name='Limite d\'étudiants'
    )
    limite_transactions_mois = models.IntegerField(
        default=1000,
        verbose_name='Limite de transactions par mois'
    )
    
    class Meta:
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.etablissement.nom} - {self.get_type_display()}"
    
    @property
    def is_actif(self):
        """Vérifie si l'abonnement est actif"""
        from django.utils import timezone
        if self.statut != StatutAbonnement.ACTIF:
            return False
        if self.date_fin and self.date_fin < timezone.now().date():
            return False
        return True
    
    def save(self, *args, **kwargs):
        """Surcharge pour définir les limites selon le type"""
        limites = {
            TypeAbonnement.GRATUIT: {'etudiants': 50, 'transactions': 100},
            TypeAbonnement.BASIQUE: {'etudiants': 500, 'transactions': 5000},
            TypeAbonnement.PREMIUM: {'etudiants': 2000, 'transactions': 20000},
            TypeAbonnement.ENTERPRISE: {'etudiants': -1, 'transactions': -1},  # -1 = illimité
        }
        
        if self.type in limites:
            limites_config = limites[self.type]
            if limites_config['etudiants'] != -1:
                self.limite_etudiants = limites_config['etudiants']
            if limites_config['transactions'] != -1:
                self.limite_transactions_mois = limites_config['transactions']
        
        super().save(*args, **kwargs)


class Facture(models.Model):
    """
    Modèle représentant une facture d'abonnement
    """
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.CASCADE,
        related_name='factures',
        verbose_name='Abonnement'
    )
    numero_facture = models.CharField(max_length=50, unique=True, verbose_name='Numéro de facture')
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant'
    )
    devise = models.CharField(max_length=3, default='USD', verbose_name='Devise')
    date_emission = models.DateField(auto_now_add=True, verbose_name='Date d\'émission')
    date_echeance = models.DateField(verbose_name='Date d\'échéance')
    payee = models.BooleanField(default=False, verbose_name='Payée')
    date_paiement = models.DateField(null=True, blank=True, verbose_name='Date de paiement')
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.abonnement.etablissement.nom}"
