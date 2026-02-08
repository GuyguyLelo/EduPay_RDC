"""
Service pour l'envoi de SMS via l'API CinetPay SMS
Documentation: https://docs.cinetpay.com/api/1.0-fr/sms/
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CinetPaySMSService:
    """Service pour envoyer des SMS via l'API CinetPay"""
    
    SMS_API_URL = "https://api-notitia.cinetpay.com/sms/1/text/single"
    
    def __init__(self):
        """Initialise le service SMS CinetPay"""
        self.api_key = getattr(settings, 'CINETPAY_SMS_API_KEY', '')
        self.sender_id = getattr(settings, 'CINETPAY_SMS_SENDER_ID', 'EDUPAY')
        
        logger.info(f"Initialisation SMS CinetPay - API Key: {self.api_key[:10] if self.api_key else 'Non configurée'}...")
        logger.info(f"Sender ID: {self.sender_id}")
        
        if not self.api_key:
            logger.warning("Clé API SMS CinetPay non configurée")
            # Ne pas lever d'erreur pour ne pas bloquer les paiements
            # raise ValueError(
            #     "La clé API SMS CinetPay n'est pas configurée. "
            #     "Veuillez définir CINETPAY_SMS_API_KEY dans votre fichier .env. "
            #     "Pour obtenir une clé API SMS, contactez CinetPay à l'adresse support@cinetpay.com"
            # )
    
    def envoyer_sms(self, numero_telephone: str, message: str) -> dict:
        """
        Envoie un SMS via l'API CinetPay
        
        Args:
            numero_telephone: Numéro de téléphone au format international (ex: +243900000000)
            message: Message SMS à envoyer
        
        Returns:
            dict: Résultat de l'envoi avec success (bool) et message (str)
        """
        try:
            # Normaliser le numéro de téléphone (enlever le + si présent pour l'API)
            numero_normalise = numero_telephone.replace('+', '').replace(' ', '')
            
            # Préparer les données
            payload = {
                'from': self.sender_id,
                'to': [numero_normalise],
                'text': message
            }
            
            # Préparer les en-têtes
            headers = {
                'Authorization': f'App {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Envoyer la requête
            response = requests.post(
                self.SMS_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Vérifier la réponse
            if response.status_code == 200:
                # Vérifier si le SMS a été envoyé avec succès
                # Le format de réponse peut varier, adapter selon la documentation CinetPay
                if result.get('status') == 'success' or result.get('messages'):
                    logger.info(f"SMS envoyé avec succès à {numero_telephone}")
                    return {
                        'success': True,
                        'message': 'SMS envoyé avec succès'
                    }
                else:
                    error_msg = result.get('error', 'Erreur lors de l\'envoi du SMS')
                    logger.error(f"Erreur CinetPay SMS: {error_msg}")
                    return {
                        'success': False,
                        'message': error_msg
                    }
            else:
                error_msg = result.get('error', f'Erreur HTTP {response.status_code}')
                logger.error(f"Erreur HTTP lors de l'envoi du SMS: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }
        
        except requests.exceptions.RequestException as e:
            error_message = f"Erreur de connexion à l'API SMS: {str(e)}"
            logger.exception(f"Erreur lors de l'envoi du SMS à {numero_telephone}: {error_message}")
            return {
                'success': False,
                'message': 'Erreur de connexion à l\'API SMS'
            }
        
        except Exception as e:
            error_message = f"Erreur inattendue: {str(e)}"
            logger.exception(f"Erreur inattendue lors de l'envoi du SMS: {error_message}")
            return {
                'success': False,
                'message': 'Une erreur inattendue s\'est produite'
            }
    
    def envoyer_confirmation_paiement(self, paiement) -> dict:
        """
        Envoie un SMS de confirmation de paiement
        
        Args:
            paiement: Instance du modèle Paiement
        
        Returns:
            dict: Résultat de l'envoi
        """
        # Récupérer le numéro de téléphone
        numero_telephone = paiement.numero_telephone
        
        # Si pas de numéro dans le paiement, essayer de le récupérer depuis l'étudiant
        if not numero_telephone and hasattr(paiement.etudiant, 'telephone'):
            numero_telephone = paiement.etudiant.telephone
        
        if not numero_telephone:
            logger.warning(f"Aucun numéro de téléphone disponible pour le paiement {paiement.id}")
            return {
                'success': False,
                'message': 'Aucun numéro de téléphone disponible'
            }
        
        # Préparer le message SMS
        date_str = paiement.date_paiement.strftime('%d/%m/%Y %H:%M') if paiement.date_paiement else 'N/A'
        reference = paiement.reference_flutterwave or paiement.transaction_id or f"REC-{paiement.id:06d}"
        
        message = (
            f"EDUPAY RDC - Paiement confirme\n"
            f"Montant: {paiement.montant} {paiement.devise}\n"
            f"Frais: {paiement.frais.nom_frais}\n"
            f"Ref: {reference}\n"
            f"Date: {date_str}\n"
            f"Merci pour votre confiance!"
        )
        
        # Envoyer le SMS
        return self.envoyer_sms(numero_telephone, message)


