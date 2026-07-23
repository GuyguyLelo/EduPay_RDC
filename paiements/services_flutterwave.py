"""
Service pour l'intégration Flutterwave
Documentation: https://developer.flutterwave.com/docs/
"""
import logging
import os
from django.conf import settings
from django.urls import reverse
from .models import Paiement, StatutPaiement

logger = logging.getLogger(__name__)

try:
    from rave_python import Rave
    RAVE_AVAILABLE = True
except ImportError:
    RAVE_AVAILABLE = False
    logger.warning("Rave Python non disponible")


class FlutterwaveService:
    """Service pour gérer les paiements via Flutterwave"""
    
    def __init__(self):
        """Initialise le service Flutterwave"""
        self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', '')
        self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
        self.environment = getattr(settings, 'FLUTTERWAVE_ENV', 'test')  # test ou prod
        
        if not self.public_key or not self.secret_key:
            logger.warning("Clés Flutterwave non configurées, utilisation des clés par défaut")
            # Clés de test par défaut
            self.public_key = 'FLWPUBK_TEST-XXXXXXXXXXXXXXXXXXXXXXXXXXXXX-X'
            self.secret_key = 'FLWSECK_TEST-XXXXXXXXXXXXXXXXXXXXXXXXXXXXX-X'
        
        logger.info(f"Service Flutterwave initialisé (environnement: {self.environment})")
    
    def _get_return_url(self, paiement_id):
        """Génère l'URL de retour"""
        try:
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            return_url = reverse('paiements_templates:paiement_success', args=[paiement_id])
            return f"{site_url}{return_url}"
        except Exception as e:
            logger.warning(f"Impossible de générer l'URL de retour: {e}")
            return f"http://localhost:8000/paiement/success/{paiement_id}/"
    
    def _get_notify_url(self):
        """Génère l'URL de notification (webhook)"""
        try:
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            notify_url = reverse('paiements:webhook_flutterwave')
            return f"{site_url}{notify_url}"
        except Exception as e:
            logger.warning(f"Impossible de générer l'URL de notification: {e}")
            return f"http://localhost:8000/api/paiements/webhook/flutterwave/"
    
    def initier_paiement(self, paiement: Paiement, redirect_url=None):
        """Initie un paiement via Flutterwave"""
        try:
            if not RAVE_AVAILABLE:
                return {
                    'success': False,
                    'error': 'SDK Flutterwave non disponible. Installez-le avec: pip install rave_python'
                }
            
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = float(paiement.montant)
            
            # Préparer les données pour Flutterwave
            data = {
                'tx_ref': transaction_id,
                'amount': amount,
                'currency': paiement.devise,
                'payment_options': 'card, mobilemoneyfr, ussd',
                'redirect_url': redirect_url or self._get_return_url(paiement.id),
                'customer': {
                    'email': paiement.etudiant.user.email if hasattr(paiement.etudiant, 'user') else 'test@example.com',
                    'phonenumber': paiement.numero_telephone or '',
                    'name': paiement.etudiant.nom_complet or 'Test User'
                },
                'customizations': {
                    'title': 'EduPay RDC',
                    'description': f"Paiement {paiement.frais.nom_frais}",
                    'logo': ''
                },
                'meta': {
                    'paiement_id': str(paiement.id)
                }
            }
            
            logger.info(f"Initialisation paiement Flutterwave: {data}")
            
            # Utiliser le SDK Flutterwave
            from rave_python import Rave
            rave = Rave(self.public_key, self.secret_key)
            
            response = rave.Payment.initiate(data)
            
            logger.info(f"Réponse Flutterwave: {response}")
            
            if response and response.get('status') == 'success':
                payment_url = response.get('data', {}).get('link')
                if payment_url:
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'payment_url': payment_url,
                        'message': 'Paiement initialisé avec succès'
                    }
            
            return {
                'success': False,
                'error': response.get('message', 'Erreur lors de l\'initialisation du paiement'),
                'details': response
            }
            
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
