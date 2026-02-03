"""
Utilitaires pour les paiements
"""
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from .models import Paiement, StatutPaiement


def calculer_commission(montant: Decimal, taux: Decimal = Decimal('2.0')) -> Decimal:
    """
    Calcule la commission de la plateforme
    
    Args:
        montant: Montant du paiement
        taux: Taux de commission en pourcentage (défaut: 2%)
    
    Returns:
        Decimal: Montant de la commission
    """
    return (montant * taux) / 100


def generer_reference_paiement(paiement: Paiement) -> str:
    """
    Génère une référence unique pour un paiement
    
    Args:
        paiement: Instance du modèle Paiement
    
    Returns:
        str: Référence unique
    """
    timestamp = int(paiement.date_creation.timestamp())
    return f"EDUPAY_{paiement.id}_{timestamp}"


def formater_montant(montant: Decimal, devise: str) -> str:
    """
    Formate un montant avec sa devise
    
    Args:
        montant: Montant à formater
        devise: Code devise (CDF, USD)
    
    Returns:
        str: Montant formaté
    """
    if devise == 'CDF':
        return f"{montant:,.0f} CDF"
    elif devise == 'USD':
        return f"${montant:,.2f}"
    else:
        return f"{montant} {devise}"


def get_paiement_urls(paiement_id: int) -> dict:
    """
    Retourne toutes les URLs pour un paiement
    
    Args:
        paiement_id: ID du paiement
    
    Returns:
        dict: Dictionnaire contenant toutes les URLs
    """
    try:
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        return {
            'return_url': f"{site_url}{reverse('paiements_templates:paiement_success', args=[paiement_id])}",
            'notify_url': f"{site_url}{reverse('paiements:webhook_cinetpay')}",
            'cancel_url': f"{site_url}{reverse('paiements_templates:paiement_cancel', args=[paiement_id])}",
        }
    except Exception as e:
        # Fallback en cas d'erreur
        return {
            'return_url': f"http://localhost:8000/paiement/success/{paiement_id}/",
            'notify_url': f"http://localhost:8000/api/paiements/webhook/cinetpay/",
            'cancel_url': f"http://localhost:8000/paiement/cancel/{paiement_id}/",
        }

