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
        
        # URLs de l'API CinetPay
        if self.environment == 'prod':
            self.base_url = 'https://api.cinetpay.com/v1'
            self.checkout_url = 'https://api-checkout.cinetpay.com/v2'
        else:
            self.base_url = 'https://api-sandbox.cinetpay.com/v1'
            self.checkout_url = 'https://api-checkout-sandbox.cinetpay.com/v2'
        
        if not self.api_key or not self.site_id:
            logger.warning("Clés CinetPay non configurées")
            raise ValueError(
                "Les clés CinetPay ne sont pas configurées. "
                "Veuillez définir CINETPAY_API_KEY et CINETPAY_SITE_ID dans votre fichier .env. "
                "Consultez env.example pour un exemple de configuration."
            )
        
        logger.info(f"Service CinetPay initialisé (environnement: {self.environment})")
    
    def _convert_operateur(self, operateur: str) -> str:
        """
        Convertit l'opérateur en format CinetPay
        
        Args:
            operateur: Opérateur (MPESA, ORANGE, AIRTEL, MTN, MOOV)
        
        Returns:
            str: Code opérateur CinetPay
        """
        mapping = {
            'MPESA': 'MPESA',
            'ORANGE': 'ORANGE',
            'AIRTEL': 'AIRTEL',
            'MTN': 'MTN',
            'MOOV': 'MOOV'
        }
        return mapping.get(operateur.upper(), 'ORANGE')
    
    def _get_operateur_display(self, operateur: str) -> str:
        """
        Retourne le nom d'affichage de l'opérateur
        
        Args:
            operateur: Code opérateur (MPESA, ORANGE, etc.)
        
        Returns:
            str: Nom d'affichage de l'opérateur
        """
        mapping = {
            'MPESA': 'M-Pesa',
            'ORANGE': 'Orange Money',
            'AIRTEL': 'Airtel Money',
            'MTN': 'MTN Mobile Money',
            'MOOV': 'Moov Money'
        }
        return mapping.get(operateur.upper(), operateur)
    
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
        """
        Retourne toutes les URLs pour un paiement
        
        Args:
            paiement_id: ID du paiement
            
        Returns:
            dict: Dictionnaire contenant toutes les URLs
        """
        return {
            'return_url': self._get_return_url(paiement_id),
            'notify_url': self._get_notify_url(),
            'cancel_url': self._get_cancel_url(paiement_id),
        }
    
    def initier_paiement_mobile_money(self, paiement: Paiement, numero_telephone: str, operateur: str):
        """
        Initie un paiement Mobile Money via CinetPay
        
        Args:
            paiement: Instance du modèle Paiement
            numero_telephone: Numéro de téléphone du payeur
            operateur: Opérateur Mobile Money
        
        Returns:
            dict: Réponse de CinetPay avec les détails de la transaction
        """
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = float(paiement.montant)
            
            # Préparer les données pour l'initialisation du paiement Mobile Money
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
                # Champs spécifiques pour le mode Seamless
                'channels': 'ALL',
                'lang': 'fr'
            }
            
            # Faire l'appel API avec requests
            response = requests.post(
                f"{self.base_url}/payment",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            logger.info(f"Réponse CinetPay pour paiement {paiement.id}: {response.status_code} - {response.text}")
            
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
                logger.error(f"Erreur API CinetPay pour paiement {paiement.id}: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Erreur API: {response.status_code}',
                    'details': response.text
                }
            
            # La réponse du SDK peut être un dict ou un objet, vérifier le format
            if isinstance(response, dict):
                result_data = response
            else:
                # Si c'est un objet, essayer de le convertir en dict
                try:
                    result_data = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result_data = {}
            
            # Vérifier si le paiement a été initialisé avec succès
            # Le format de réponse peut varier, adapter selon la documentation
            code = result_data.get('code', result_data.get('status', ''))
            
            if code == '201' or result_data.get('status') == 'SUCCESS' or 'payment_url' in str(result_data).lower():
                # Paiement initié avec succès
                # Extraire les données importantes de la réponse CinetPay
                data_dict = result_data.get('data', {}) if isinstance(result_data.get('data'), dict) else {}
                
                # CinetPay retourne 'payment_token' et 'payment_url' dans 'data'
                payment_token = data_dict.get('payment_token', '')
                payment_url = data_dict.get('payment_url', '')
                
                # Fallback: chercher dans result_data directement
                if not payment_url:
                    payment_url = result_data.get('payment_url', '')
                if not payment_token:
                    payment_token = result_data.get('payment_token', '') or result_data.get('token', '')
                
                # Si payment_url n'est pas trouvé, chercher dans la réponse brute
                if not payment_url:
                    # Le SDK peut retourner l'URL directement dans certaines propriétés
                    if hasattr(response, 'payment_url'):
                        payment_url = response.payment_url
                    elif isinstance(response, str):
                        # Peut-être que la réponse est une URL directement
                        if 'http' in response:
                            payment_url = response
                
                # Mettre à jour le paiement
                paiement.reference_flutterwave = transaction_id  # Réutiliser le champ pour la référence CinetPay
                # Utiliser payment_token si disponible, sinon transaction_id
                paiement.transaction_id = payment_token if payment_token else transaction_id
                paiement.numero_telephone = numero_telephone
                paiement.operateur = operateur
                paiement.methode_paiement = 'MOBILE_MONEY'
                # Stocker aussi l'URL de paiement si disponible (pour redirection directe si nécessaire)
                if payment_url:
                    # Stocker dans message_erreur pour pouvoir l'utiliser plus tard si nécessaire
                    paiement.message_erreur = payment_url
                paiement.save()
                
                logger.info(f"Paiement CinetPay {paiement.id} initié avec succès. Transaction ID: {transaction_id}")
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'token': payment_token,
                    'payment_url': payment_url,
                    'message': 'Paiement initié avec succès. Veuillez confirmer sur votre téléphone.',
                    'data': result_data
                }
            else:
                error_message = result_data.get('message', result_data.get('description', 'Erreur lors de l\'initiation du paiement'))
                error_code = result_data.get('code', '')
                
                # Détecter l'erreur spécifique d'opérateur indisponible
                error_lower = error_message.lower()
                if 'operateur' in error_lower or 'operator' in error_lower or 'indisponible' in error_lower or 'unavailable' in error_lower:
                    # Message personnalisé pour opérateur indisponible
                    operateur_display = self._get_operateur_display(operateur)
                    error_message = f"L'opérateur {operateur_display} n'est pas disponible pour votre compte marchand. Veuillez choisir un autre opérateur ou contacter le support CinetPay pour activer cet opérateur."
                    logger.warning(f"Opérateur {operateur} indisponible pour paiement {paiement.id}")
                elif 'currency' in error_lower or 'devise' in error_lower:
                    # Erreur de devise
                    error_message = f"La devise {paiement.devise} n'est pas supportée. Veuillez contacter le support."
                    logger.warning(f"Devise {paiement.devise} non supportée pour paiement {paiement.id}")
                
                logger.error(f"Erreur CinetPay pour paiement {paiement.id}: code={error_code}, message={error_message}")
                
                # Ne pas marquer comme FAILED si c'est juste un problème d'opérateur
                # L'utilisateur peut réessayer avec un autre opérateur
                if 'operateur' in error_lower or 'operator' in error_lower or 'indisponible' in error_lower:
                    paiement.statut = StatutPaiement.PENDING  # Garder en PENDING pour permettre un nouvel essai
                else:
                    paiement.statut = StatutPaiement.FAILED
                
                paiement.message_erreur = error_message
                paiement.save()
                
                return {
                    'success': False,
                    'message': error_message,
                    'code': error_code,
                    'retry_possible': 'operateur' in error_lower or 'operator' in error_lower
                }
        
        except Exception as e:
            error_message = f"Erreur inattendue: {str(e)}"
            logger.exception(f"Erreur inattendue pour paiement {paiement.id}: {error_message}")
            
            paiement.statut = StatutPaiement.FAILED
            paiement.message_erreur = error_message
            paiement.save()
            
            return {
                'success': False,
                'message': 'Une erreur inattendue s\'est produite'
            }
    
    def initier_paiement_carte_bancaire(self, paiement: Paiement, email: str, redirect_url: str = None):
        """
        Initie un paiement par carte bancaire via CinetPay
        
        Args:
            paiement: Instance du modèle Paiement
            email: Email du payeur
            redirect_url: URL de redirection après paiement (optionnel)
        
        Returns:
            dict: Réponse de CinetPay avec le lien de paiement
        """
        try:
            transaction_id = f"EDUPAY_{paiement.id}_{int(paiement.date_creation.timestamp())}"
            amount = float(paiement.montant)
            
            data = {
                'amount': amount,
                'currency': paiement.devise,
                'transaction_id': transaction_id,
                'description': f"Paiement {paiement.frais.nom_frais} - {paiement.frais.etablissement.nom}",
                'return_url': redirect_url or self._get_return_url(paiement.id),
                'notify_url': self._get_notify_url(),
                'cancel_url': self._get_cancel_url(paiement.id),
                'customer_name': paiement.etudiant.nom_complet.split()[0] if paiement.etudiant.nom_complet else paiement.etudiant.prenom,
                'customer_surname': paiement.etudiant.prenom if paiement.etudiant.prenom else paiement.etudiant.nom_complet.split()[-1] if paiement.etudiant.nom_complet else "",
                'customer_email': paiement.etudiant.user.email if hasattr(paiement.etudiant, 'user') else '',
                # Champs supplémentaires requis par CinetPay
                'customer_address': 'Kinshasa, RDC',
                'customer_city': 'Kinshasa',
                'customer_country': 'CD',
                'customer_state': 'Kinshasa',
                'customer_zip_code': '00000',
                # Champs spécifiques pour le mode Seamless
                'channels': 'ALL',
                'lang': 'fr'
            }
            
            response = self.client.PaymentInitialization(data)
            
            # Traiter la réponse (même logique que pour Mobile Money)
            if isinstance(response, dict):
                result_data = response
            else:
                try:
                    result_data = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result_data = {}
            
            code = result_data.get('code', result_data.get('status', ''))
            
            if code == '201' or result_data.get('status') == 'SUCCESS' or 'payment_url' in str(result_data).lower():
                # Extraire les données de la réponse CinetPay
                data_dict = result_data.get('data', {}) if isinstance(result_data.get('data'), dict) else {}
                
                # CinetPay retourne 'payment_token' et 'payment_url' dans 'data'
                payment_token = data_dict.get('payment_token', '')
                payment_url = data_dict.get('payment_url', '')
                
                # Fallback: chercher dans result_data directement
                if not payment_url:
                    payment_url = result_data.get('payment_url', '')
                if not payment_token:
                    payment_token = result_data.get('payment_token', '') or result_data.get('token', '')
                
                if not payment_url and hasattr(response, 'payment_url'):
                    payment_url = response.payment_url
                
                paiement.reference_flutterwave = transaction_id
                # Utiliser payment_token si disponible, sinon transaction_id
                paiement.transaction_id = payment_token if payment_token else transaction_id
                paiement.email_paiement = email
                paiement.methode_paiement = 'CARTE_BANCAIRE'
                # Stocker aussi l'URL de paiement si disponible
                if payment_url:
                    paiement.message_erreur = payment_url
                paiement.save()
                
                logger.info(f"Paiement par carte CinetPay {paiement.id} initié avec succès. Transaction ID: {transaction_id}")
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'token': payment_token,
                    'payment_link': payment_url,
                    'message': 'Paiement par carte initié avec succès',
                    'data': result_data
                }
            else:
                error_message = result_data.get('message', 'Erreur lors de l\'initiation du paiement')
                logger.error(f"Erreur CinetPay pour paiement {paiement.id}: {error_message}")
                
                paiement.statut = StatutPaiement.FAILED
                paiement.message_erreur = error_message
                paiement.save()
                
                return {
                    'success': False,
                    'message': error_message
                }
        
        except Exception as e:
            error_message = f"Erreur inattendue: {str(e)}"
            logger.exception(f"Erreur inattendue pour paiement {paiement.id}: {error_message}")
            
            paiement.statut = StatutPaiement.FAILED
            paiement.message_erreur = error_message
            paiement.save()
            
            return {
                'success': False,
                'message': 'Une erreur inattendue s\'est produite'
            }
    
    def initier_paiement_qr_code(self, paiement: Paiement, email: str, redirect_url: str = None):
        """
        Initie un paiement par QR Code via CinetPay
        
        Args:
            paiement: Instance du modèle Paiement
            email: Email du payeur
            redirect_url: URL de redirection après paiement (optionnel)
        
        Returns:
            dict: Réponse avec le QR Code et le lien de paiement
        """
        # Pour le QR Code, on utilise la même méthode que pour la carte bancaire
        # CinetPay génère automatiquement un QR Code pour le lien de paiement
        result = self.initier_paiement_carte_bancaire(paiement, email, redirect_url)
        
        if result.get('success'):
            # Marquer comme QR Code et stocker le lien pour génération du QR
            paiement.methode_paiement = 'QR_CODE'
            payment_link = result.get('payment_link') or result.get('payment_url')
            if payment_link:
                # Stocker le lien dans message_erreur pour les QR Codes (champ réutilisé)
                paiement.message_erreur = payment_link
                # Aussi stocker dans reference_flutterwave si c'est une URL
                if payment_link.startswith('http'):
                    paiement.reference_flutterwave = payment_link
            paiement.save()
            
            result['message'] = 'QR Code généré avec succès'
            result['qr_code_data'] = result.get('payment_link')
        
        return result
    
    def verifier_paiement(self, paiement: Paiement):
        """
        Vérifie le statut d'un paiement et met à jour son statut
        
        Args:
            paiement: Instance du modèle Paiement
        
        Returns:
            dict: Résultat de la vérification
        """
        if not paiement.transaction_id:
            return {
                'success': False,
                'message': 'Aucun ID de transaction disponible'
            }
        
        try:
            # Utiliser la méthode de vérification par transaction_id
            # Si transaction_id est un payment_token (long), utiliser TransactionVerfication_token
            # Sinon, utiliser TransactionVerfication_trx avec la référence de transaction
            transaction_ref = paiement.reference_flutterwave or paiement.transaction_id
            
            # Si transaction_id ressemble à un payment_token (long), utiliser la vérification par token
            if paiement.transaction_id and len(paiement.transaction_id) > 50:
                # C'est probablement un payment_token
                response = self.client.TransactionVerfication_token(paiement.transaction_id)
            else:
                # C'est une référence de transaction
                response = self.client.TransactionVerfication_trx(transaction_ref)
            
            logger.info(f"Réponse vérification CinetPay pour paiement {paiement.id}: {response}")
            
            # Traiter la réponse
            if isinstance(response, dict):
                result_data = response
            else:
                try:
                    result_data = response.__dict__ if hasattr(response, '__dict__') else {}
                except:
                    result_data = {}
            
            code = result_data.get('code', result_data.get('status', ''))
            message = result_data.get('message', '')
            
            # Les codes CinetPay :
            # - '00' : Paiement accepté
            # - '662' : En attente de paiement (WAITING_CUSTOMER_PAYMENT)
            # - Autres codes : Erreurs ou autres statuts
            
            if code == '00' or code == 'ACCEPTED' or result_data.get('status') == 'ACCEPTED':
                # Paiement trouvé et accepté
                payment_data = result_data.get('data', {}) if isinstance(result_data.get('data'), dict) else result_data
                status = str(payment_data.get('status', '')).upper()
                
                if status == 'ACCEPTED' or status == 'SUCCESS':
                    paiement.statut = StatutPaiement.SUCCESS
                    if not paiement.date_paiement:
                        from django.utils import timezone
                        paiement.date_paiement = timezone.now()
                    
                    # Calculer et sauvegarder la commission
                    commission_rate = getattr(settings, 'COMMISSION_RATE', Decimal('2.0'))
                    paiement.taux_commission = commission_rate
                    paiement.commission_plateforme = paiement.calculer_commission()
                    paiement.save()
                    
                    logger.info(f"Paiement {paiement.id} confirmé avec succès")
                elif status == 'REFUSED' or status == 'FAILED':
                    paiement.statut = StatutPaiement.FAILED
                    paiement.message_erreur = payment_data.get('message', 'Paiement refusé')
                    paiement.save()
                    logger.warning(f"Paiement {paiement.id} refusé")
                else:
                    logger.info(f"Paiement {paiement.id} toujours en attente")
                
                return {
                    'success': True,
                    'status': status,
                    'paiement_status': paiement.statut,
                    'data': payment_data
                }
            elif code == '662' or message == 'WAITING_CUSTOMER_PAYMENT':
                # Paiement en attente - statut normal
                payment_data = result_data.get('data', {}) if isinstance(result_data.get('data'), dict) else result_data
                status = str(payment_data.get('status', 'PENDING')).upper()
                
                # S'assurer que le statut reste PENDING
                paiement.statut = StatutPaiement.PENDING
                paiement.save()
                
                logger.info(f"Paiement {paiement.id} en attente de confirmation (WAITING_CUSTOMER_PAYMENT)")
                
                return {
                    'success': True,
                    'status': 'PENDING',
                    'paiement_status': paiement.statut,
                    'message': 'Paiement en attente de confirmation',
                    'data': payment_data
                }
            else:
                # Autre code d'erreur
                error_message = result_data.get('message', 'Impossible de vérifier le paiement')
                logger.warning(f"Code de vérification CinetPay inattendu pour paiement {paiement.id}: code={code}, message={error_message}")
                
                return {
                    'success': False,
                    'message': error_message,
                    'code': code
                }
        
        except Exception as e:
            logger.exception(f"Erreur lors de la vérification du paiement {paiement.id}: {str(e)}")
            return {
                'success': False,
                'message': f'Erreur lors de la vérification: {str(e)}'
            }
    
    def valider_webhook(self, payload: dict) -> bool:
        """
        Valide un webhook CinetPay
        
        Args:
            payload: Données du webhook
        
        Returns:
            bool: True si le webhook est valide
        """
        # CinetPay envoie les données avec une signature
        # Pour l'instant, on accepte tous les webhooks en mode test
        if self.environment == 'test':
            return True
        
        # En production, valider la signature selon la documentation CinetPay
        # Consultez la documentation pour la validation des signatures en production
        return True
