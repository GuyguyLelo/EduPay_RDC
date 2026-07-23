"""
Service pour l'intégration CinetPay avec le SDK Python officiel
Documentation: https://docs.cinetpay.com/api/1.0-fr/sdk/python
"""
import logging
from django.conf import settings
from django.urls import reverse
from .models import Paiement, StatutPaiement

try:
    from cinetpay_sdk.s_d_k import Cinetpay
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    logger.warning("SDK CinetPay non disponible")

logger = logging.getLogger(__name__)


class CinetPayService:
    """Service pour gérer les paiements via CinetPay (SDK Python officiel)"""
    
    def __init__(self):
        """Initialise le service CinetPay avec le SDK Python"""
        self.api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        self.site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        self.environment = getattr(settings, 'CINETPAY_ENV', 'test')  # test ou prod
        
        if not SDK_AVAILABLE:
            raise ValueError(
                "Le SDK CinetPay n'est pas installé. "
                "Installez-le avec: pip install cinetpay-sdk"
            )
        
        if not self.api_key or not self.site_id:
            logger.warning("Clés CinetPay non configurées")
            raise ValueError(
                "Les clés CinetPay ne sont pas configurées. "
                "Veuillez définir CINETPAY_API_KEY et CINETPAY_SITE_ID dans votre fichier .env. "
                "Consultez env.example pour un exemple de configuration."
            )
        
        # Initialiser le client CinetPay
        self.client = Cinetpay(self.api_key, self.site_id)
        logger.info(f"Service CinetPay initialisé avec SDK (environnement: {self.environment})")
    
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
        """Initie un paiement Mobile Money via CinetPay SDK"""
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = int(float(paiement.montant))
            
            # Préparer les données pour le SDK CinetPay
            data = {
                'amount': amount,
                'currency': paiement.devise,
                'transaction_id': transaction_id,
                'description': f"Paiement {paiement.frais.nom_frais} - {paiement.frais.etablissement.nom}",
                'return_url': self._get_return_url(paiement.id),
                'notify_url': self._get_notify_url(),
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
            
            # Utiliser le SDK CinetPay
            response = self.client.PaymentInitialization(data)
            
            logger.info(f"Réponse CinetPay SDK pour paiement {paiement.id}: {response}")
            
            # Traiter la réponse du SDK
            if isinstance(response, dict):
                result = response
            else:
                try:
                    result = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result = {}
            
            # Vérifier si le paiement a été initialisé avec succès
            code = result.get('code', result.get('status', ''))
            
            if code == '201' or result.get('status') == 'SUCCESS' or 'payment_url' in str(result).lower():
                # Paiement initié avec succès
                data_dict = result.get('data', {}) if isinstance(result.get('data'), dict) else {}
                payment_url = data_dict.get('payment_url', '') or result.get('payment_url', '')
                
                logger.info(f"Paiement {paiement.id} initialisé avec succès via SDK")
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': payment_url,
                    'message': result.get('message', 'Paiement initialisé'),
                    'data': result
                }
            else:
                error_message = result.get('message', result.get('description', 'Échec de l\'initialisation'))
                logger.error(f"Échec initialisation paiement {paiement.id}: {error_message}")
                return {
                    'success': False,
                    'error': error_message,
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement {paiement.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
    
    def initier_paiement_carte_bancaire(self, paiement: Paiement, redirect_url=None):
        """Initie un paiement par carte bancaire via CinetPay SDK"""
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = int(float(paiement.montant))
            
            # Préparer les données pour le SDK CinetPay
            data = {
                'amount': amount,
                'currency': paiement.devise,
                'transaction_id': transaction_id,
                'description': f"Paiement {paiement.frais.nom_frais} - {paiement.frais.etablissement.nom}",
                'return_url': redirect_url or self._get_return_url(paiement.id),
                'notify_url': self._get_notify_url(),
                'customer_name': paiement.etudiant.nom_complet.split()[0] if paiement.etudiant.nom_complet else paiement.etudiant.prenom,
                'customer_surname': paiement.etudiant.prenom if paiement.etudiant.prenom else paiement.etudiant.nom_complet.split()[-1] if paiement.etudiant.nom_complet else "",
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
            
            # Utiliser le SDK CinetPay
            response = self.client.PaymentInitialization(data)
            
            logger.info(f"Réponse CinetPay SDK pour paiement carte {paiement.id}: {response}")
            
            # Traiter la réponse du SDK
            if isinstance(response, dict):
                result = response
            else:
                try:
                    result = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result = {}
            
            # Vérifier si le paiement a été initialisé avec succès
            code = result.get('code', result.get('status', ''))
            
            if code == '201' or result.get('status') == 'SUCCESS' or 'payment_url' in str(result).lower():
                # Paiement initié avec succès
                data_dict = result.get('data', {}) if isinstance(result.get('data'), dict) else {}
                payment_url = data_dict.get('payment_url', '') or result.get('payment_url', '')
                
                logger.info(f"Paiement carte {paiement.id} initialisé avec succès via SDK")
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': payment_url,
                    'message': result.get('message', 'Paiement initialisé'),
                    'data': result
                }
            else:
                error_message = result.get('message', result.get('description', 'Échec de l\'initialisation'))
                logger.error(f"Échec initialisation paiement carte {paiement.id}: {error_message}")
                return {
                    'success': False,
                    'error': error_message,
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"Exception lors de l'initialisation du paiement carte {paiement.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
    
    def verifier_statut_paiement(self, transaction_id: str):
        """Vérifie le statut d'un paiement via CinetPay SDK"""
        try:
            # Utiliser le SDK CinetPay pour vérifier le statut
            response = self.client.getPayStatus(transaction_id, self.site_id)
            
            logger.info(f"Réponse vérification CinetPay SDK pour {transaction_id}: {response}")
            
            # Traiter la réponse du SDK
            if isinstance(response, dict):
                result = response
            else:
                try:
                    result = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result = {}
            
            # Vérifier le statut du paiement
            code = result.get('code', result.get('status', ''))
            
            if code == '00' or result.get('status') == 'ACCEPTED':
                return {
                    'success': True,
                    'status': result.get('status', 'ACCEPTED'),
                    'message': result.get('message', 'Paiement accepté'),
                    'data': result
                }
            else:
                error_message = result.get('message', result.get('description', 'Impossible de vérifier le paiement'))
                logger.warning(f"Statut paiement non confirmé: {error_message}")
                return {
                    'success': False,
                    'error': error_message,
                    'details': result
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du paiement {transaction_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }
