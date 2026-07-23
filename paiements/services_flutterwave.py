"""
Service pour l'intégration Flutterwave
Documentation: https://developer.flutterwave.com/docs/
"""
import logging
import os
import requests
from django.conf import settings
from django.urls import reverse
from .models import Paiement, StatutPaiement

logger = logging.getLogger(__name__)


class FlutterwaveService:
    """Service pour gérer les paiements via Flutterwave (API REST)"""
    
    def __init__(self):
        """Initialise le service Flutterwave"""
        self.public_key = getattr(settings, 'RAVE_PUBLIC_KEY', '')
        self.secret_key = getattr(settings, 'RAVE_SECRET_KEY', '')
        self.environment = getattr(settings, 'FLUTTERWAVE_ENV', 'test')  # test ou prod
        
        # URLs de l'API Flutterwave selon l'environnement
        if self.environment == 'prod':
            self.base_url = 'https://api.flutterwave.com/v3'
        else:
            self.base_url = 'https://ravesandboxapi.flutterwave.com/v3'
        
        if not self.public_key or not self.secret_key:
            logger.warning("Clés Flutterwave non configurées")
            raise ValueError(
                "Les clés Flutterwave ne sont pas configurées. "
                "Veuillez définir RAVE_PUBLIC_KEY et RAVE_SECRET_KEY dans votre fichier .env. "
                "Consultez env.example pour un exemple de configuration."
            )
        
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
        """Initie un paiement via Flutterwave API REST"""
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = int(float(paiement.montant))
            
            # Préparer les données pour Flutterwave API v3
            # Options de paiement pour la RDC: carte, mobilemoneycd (Orange Money, Airtel Money, M-Pesa)
            data = {
                'tx_ref': transaction_id,
                'amount': amount,
                'currency': paiement.devise,
                'payment_options': 'card, mobilemoneycd, ussd, banktransfer',
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
                    'paiement_id': str(paiement.id),
                    'customer_name': paiement.etudiant.nom_complet or 'Test User'
                }
            }
            
            logger.info(f"Initialisation paiement Flutterwave: {data}")
            
            # Utiliser l'API REST Flutterwave
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.base_url}/payments",
                json=data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Réponse Flutterwave: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    payment_url = result.get('data', {}).get('link')
                    if payment_url:
                        return {
                            'success': True,
                            'transaction_id': transaction_id,
                            'payment_url': payment_url,
                            'message': 'Paiement initialisé avec succès'
                        }
            
            return {
                'success': False,
                'error': response.text if response.status_code != 200 else 'Erreur lors de l\'initialisation du paiement',
                'details': response.text
            }
            
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
