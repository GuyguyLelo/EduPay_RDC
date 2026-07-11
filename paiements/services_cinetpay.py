"""
Service pour l'intégration CinetPay avec l'API REST
Documentation: https://docs.cinetpay.com/api/1.0-fr/
"""
import logging
import requests
import json
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from .models import Paiement, StatutPaiement

logger = logging.getLogger(__name__)


class CinetPayService:
    """Service pour gérer les paiements via CinetPay (API REST)"""
    
    def __init__(self):
        """Initialise le service CinetPay avec l'API REST"""
        self.api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        self.site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        self.environment = getattr(settings, 'CINETPAY_ENV', 'test')  # test ou prod
        
        # URLs de l'API CinetPay - utiliser l'URL principale
        self.base_url = 'https://api.cinetpay.com/v1'
        self.checkout_url = 'https://api.cinetpay.com/v2'
        
        if not self.api_key or not self.site_id:
            logger.warning("Clés CinetPay non configurées")
            raise ValueError(
                "Les clés CinetPay ne sont pas configurées. "
                "Veuillez définir CINETPAY_API_KEY et CINETPAY_SITE_ID dans votre fichier .env. "
                "Consultez env.example pour un exemple de configuration."
            )
        
        logger.info(f"Service CinetPay initialisé (environnement: {self.environment})")
    
    def _convert_operateur(self, operateur: str) -> str:
        """Convertit l'opérateur en format CinetPay"""
        mapping = {
            'MPESA': 'MPESA',
            'ORANGE': 'ORANGE',
            'AIRTEL': 'AIRTEL',
            'MTN': 'MTN',
            'MOOV': 'MOOV'
        }
        return mapping.get(operateur.upper(), 'ORANGE')
    
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
            notify_url = reverse('paiements:webhook_cinetpay')
            return f"{site_url}{notify_url}"
        except Exception as e:
            logger.warning(f"Impossible de générer l'URL de notification: {e}")
            return f"http://localhost:8000/api/paiements/webhook/cinetpay/"
    
    def _get_cancel_url(self, paiement_id):
        """Génère l'URL d'annulation"""
        try:
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            cancel_url = reverse('paiements_templates:paiement_cancel', args=[paiement_id])
            return f"{site_url}{cancel_url}"
        except Exception as e:
            logger.warning(f"Impossible de générer l'URL d'annulation: {e}")
            return f"http://localhost:8000/paiement/cancel/{paiement_id}/"
    
    def get_all_urls(self, paiement_id):
        """Retourne toutes les URLs pour un paiement"""
        return {
            'return_url': self._get_return_url(paiement_id),
            'notify_url': self._get_notify_url(),
            'cancel_url': self._get_cancel_url(paiement_id),
        }
    
    def initier_paiement_mobile_money(self, paiement: Paiement, numero_telephone: str, operateur: str):
        """Initie un paiement Mobile Money via CinetPay"""
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = float(paiement.montant)
            
            # Préparer les données pour l'API CinetPay
            data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'amount': amount,
                'currency': paiement.devise,
                'transaction_id': transaction_id,
                'description': f"Paiement {paiement.frais.nom_frais} - {paiement.frais.etablissement.nom}",
                'return_url': self._get_return_url(paiement.id),
                'notify_url': self._get_notify_url(),
                'cancel_url': self._get_cancel_url(paiement.id),
                'customer_name': paiement.etudiant.nom_complet.split()[0] if paiement.etudiant.nom_complet else paiement.etudiant.prenom,
                'customer_surname': paiement.etudiant.prenom if paiement.etudiant.prenom else paiement.etudiant.nom_complet.split()[-1] if paiement.etudiant.nom_complet else "",
                'customer_phone_number': numero_telephone,
                'customer_email': paiement.etudiant.user.email if hasattr(paiement.etudiant, 'user') else '',
                # Champs supplémentaires requis par CinetPay
                'customer_address': 'Kinshasa, RDC',
                'customer_city': 'Kinshasa',
                'customer_country': 'CD',
                'customer_state': 'Kinshasa',
                'customer_zip_code': '00000',
                'channels': 'ALL',
                'lang': 'fr'
            }
            
            # Faire l'appel API avec requests
            response = requests.post(
                f"{self.checkout_url}/payment",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            logger.info(f"Réponse CinetPay pour paiement {paiement.id}: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'accepted':
                    logger.info(f"Paiement {paiement.id} initialisé avec succès")
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'payment_url': result.get('payment_url'),
                        'message': result.get('message', 'Paiement initialisé')
                    }
                else:
                    logger.error(f"Échec initialisation paiement {paiement.id}: {result}")
                    return {
                        'success': False,
                        'error': result.get('message', 'Échec de l\'initialisation'),
                        'details': result
                    }
            else:
                logger.error(f"Erreur API CinetPay pour paiement {paiement.id}: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Erreur API: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement {paiement.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
    
    def initier_paiement_carte_bancaire(self, paiement: Paiement, redirect_url=None):
        """Initie un paiement par carte bancaire via CinetPay (API REST)"""
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = float(paiement.montant)
            
            # Préparer les données pour l'API CinetPay
            data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'amount': amount,
                'currency': paiement.devise,
                'transaction_id': transaction_id,
                'description': f"Paiement {paiement.frais.nom_frais} - {paiement.frais.etablissement.nom}",
                'return_url': redirect_url or self._get_return_url(paiement.id),
                'notify_url': self._get_notify_url(),
                'customer_name': paiement.etudiant.nom_complet.split()[0] if paiement.etudiant.nom_complet else paiement.etudiant.prenom,
                'customer_surname': paiement.etudiant.prenom if paiement.etudiant.prenom else paiement.etudiant.nom_complet.split()[-1] if paiement.etudiant.nom_complet else "",
            }
            
            # Essayer plusieurs endpoints possibles
            endpoints = [
                f"{self.checkout_url}/payment/initialize",
                f"{self.checkout_url}/payment",
                f"{self.base_url}/payment/initialize",
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Tentative endpoint: {endpoint}")
                    response = requests.post(
                        endpoint,
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    logger.info(f"Réponse CinetPay pour paiement {paiement.id}: {response.status_code} depuis {endpoint}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Réponse JSON: {result}")
                        
                        # Vérifier différents formats de réponse possibles
                        if result.get('code') == '201' and result.get('data'):
                            payment_data = result['data']
                            logger.info(f"Paiement {paiement.id} initialisé avec succès")
                            return {
                                'success': True,
                                'transaction_id': transaction_id,
                                'payment_url': payment_data.get('payment_url'),
                                'message': result.get('message', 'Paiement initialisé')
                            }
                        elif result.get('status') == 'accepted':
                            logger.info(f"Paiement {paiement.id} initialisé avec succès")
                            return {
                                'success': True,
                                'transaction_id': transaction_id,
                                'payment_url': result.get('payment_url'),
                                'message': result.get('message', 'Paiement initialisé')
                            }
                        else:
                            logger.warning(f"Réponse non réussie depuis {endpoint}: {result}")
                            continue
                    else:
                        logger.warning(f"Status code {response.status_code} depuis {endpoint}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"Erreur avec endpoint {endpoint}: {e}")
                    continue
            
            # Si tous les endpoints ont échoué
            logger.error(f"Tous les endpoints ont échoué pour paiement {paiement.id}")
            return {
                'success': False,
                'error': 'Tous les endpoints CinetPay ont échoué. Vérifiez vos clés API et la configuration.'
            }
                
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement {paiement.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
    
    def verifier_statut_paiement(self, transaction_id: str):
        """Vérifie le statut d'un paiement via CinetPay (API REST)"""
        try:
            data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'transaction_id': transaction_id
            }
            
            # Essayer plusieurs endpoints possibles pour la vérification
            endpoints = [
                f"{self.checkout_url}/payment/check",
                f"{self.base_url}/payment/check",
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Tentative vérification endpoint: {endpoint}")
                    response = requests.post(
                        endpoint,
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    logger.info(f"Réponse vérification: {response.status_code} depuis {endpoint}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Réponse JSON vérification: {result}")
                        
                        if result.get('code') == '00':
                            return {
                                'success': True,
                                'status': result.get('status'),
                                'message': result.get('message'),
                                'data': result
                            }
                        else:
                            logger.warning(f"Réponse non réussie depuis {endpoint}: {result}")
                            continue
                    else:
                        logger.warning(f"Status code {response.status_code} depuis {endpoint}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"Erreur avec endpoint {endpoint}: {e}")
                    continue
            
            logger.error(f"Tous les endpoints de vérification ont échoué")
            return {
                'success': False,
                'error': 'Tous les endpoints de vérification ont échoué'
            }
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du paiement: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
