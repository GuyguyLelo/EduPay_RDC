"""
Tests pour l'app paiements
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from core.models import UserRole
from etablissements.models import Etablissement, TypeEtablissement, StatutEtablissement
from etudiants.models import Etudiant
from frais.models import Frais, Devise
from .models import Paiement, StatutPaiement
from .receipts import send_payment_confirmation_sms

User = get_user_model()


class PaiementModelTest(TestCase):
    """Tests pour le modèle Paiement"""
    
    def setUp(self):
        """Configuration initiale"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='etudiant@example.com',
            password='testpass123',
            role=UserRole.ETUDIANT
        )
        
        # Créer un établissement
        self.etablissement = Etablissement.objects.create(
            nom='Université Test',
            type=TypeEtablissement.UNIVERSITE,
            email='univ@example.com',
            telephone='+243900000000',
            adresse='Kinshasa, RDC',
            statut=StatutEtablissement.ACTIF
        )
        
        # Créer un étudiant
        self.etudiant = Etudiant.objects.create(
            user=self.user,
            nom='Doe',
            prenom='John',
            matricule='ETU001',
            etablissement=self.etablissement
        )
        
        # Créer des frais
        self.frais = Frais.objects.create(
            etablissement=self.etablissement,
            nom_frais='Frais de scolarité',
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            annee_academique='2024-2025'
        )
    
    def test_paiement_creation(self):
        """Test de création d'un paiement"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=self.frais.montant,
            devise=self.frais.devise,
            taux_commission=Decimal('2.0')
        )
        
        self.assertEqual(paiement.etudiant, self.etudiant)
        self.assertEqual(paiement.frais, self.frais)
        self.assertEqual(paiement.montant, Decimal('50000.00'))
        self.assertEqual(paiement.statut, StatutPaiement.PENDING)
    
    def test_commission_calculation(self):
        """Test du calcul de la commission"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            taux_commission=Decimal('2.0')
        )
        
        # La commission devrait être calculée automatiquement
        expected_commission = (Decimal('50000.00') * Decimal('2.0')) / 100
        self.assertEqual(paiement.commission_plateforme, expected_commission)
    
    def test_montant_etablissement(self):
        """Test du calcul du montant pour l'établissement"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            taux_commission=Decimal('2.0')
        )
        
        montant_etab = paiement.montant - paiement.commission_plateforme
        self.assertEqual(paiement.montant_etablissement, montant_etab)
    
    def test_paiement_str(self):
        """Test de la représentation string"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=Decimal('50000.00'),
            devise=Devise.CDF
        )
        
        self.assertIn('Paiement', str(paiement))
        self.assertIn('Doe', str(paiement))


class SendPaymentConfirmationSMSTest(TestCase):
    """Tests pour la fonction send_payment_confirmation_sms"""
    
    def setUp(self):
        """Configuration initiale"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='etudiant@example.com',
            password='testpass123',
            role=UserRole.ETUDIANT
        )
        
        # Créer un établissement
        self.etablissement = Etablissement.objects.create(
            nom='Université Test',
            type=TypeEtablissement.UNIVERSITE,
            email='univ@example.com',
            telephone='+243900000000',
            adresse='Kinshasa, RDC',
            statut=StatutEtablissement.ACTIF
        )
        
        # Créer un étudiant
        self.etudiant = Etudiant.objects.create(
            user=self.user,
            nom='Doe',
            prenom='John',
            matricule='ETU001',
            etablissement=self.etablissement
        )
        
        # Créer des frais
        self.frais = Frais.objects.create(
            etablissement=self.etablissement,
            nom_frais='Frais de scolarité',
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            annee_academique='2024-2025'
        )
        
        # Créer un paiement
        self.paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            statut=StatutPaiement.SUCCESS,
            numero_telephone='+243900000000',
            reference_flutterwave='REF123456',
            transaction_id='TXN123456',
            date_paiement=timezone.now()
        )
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_success(self, mock_sms_service_class):
        """Test d'envoi réussi de SMS"""
        # Mock du service SMS
        mock_sms_service = MagicMock()
        mock_sms_service_class.return_value = mock_sms_service
        mock_sms_service.envoyer_confirmation_paiement.return_value = {
            'success': True,
            'message': 'SMS envoyé avec succès'
        }
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(self.paiement)
        
        # Vérifications
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'SMS envoyé avec succès')
        mock_sms_service.envoyer_confirmation_paiement.assert_called_once_with(self.paiement)
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_failure(self, mock_sms_service_class):
        """Test d'échec d'envoi de SMS"""
        # Mock du service SMS
        mock_sms_service = MagicMock()
        mock_sms_service_class.return_value = mock_sms_service
        mock_sms_service.envoyer_confirmation_paiement.return_value = {
            'success': False,
            'message': 'Erreur lors de l\'envoi du SMS'
        }
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(self.paiement)
        
        # Vérifications
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Erreur lors de l\'envoi du SMS')
        mock_sms_service.envoyer_confirmation_paiement.assert_called_once_with(self.paiement)
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_api_key_not_configured(self, mock_sms_service_class):
        """Test quand la clé API SMS n'est pas configurée"""
        # Mock pour lever ValueError (clé API non configurée)
        mock_sms_service_class.side_effect = ValueError(
            "La clé API SMS CinetPay n'est pas configurée."
        )
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(self.paiement)
        
        # Vérifications
        self.assertFalse(result['success'])
        self.assertIn('clé API SMS', result['message'])
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_general_exception(self, mock_sms_service_class):
        """Test de gestion d'exception générale"""
        # Mock pour lever une exception générale
        mock_sms_service_class.side_effect = Exception("Erreur inattendue")
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(self.paiement)
        
        # Vérifications
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Erreur inattendue')
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_no_phone_number(self, mock_sms_service_class):
        """Test quand aucun numéro de téléphone n'est disponible"""
        # Créer un paiement sans numéro de téléphone
        paiement_sans_tel = Paiement.objects.create(
            etudiant=self.etudiant,
            frais=self.frais,
            montant=Decimal('50000.00'),
            devise=Devise.CDF,
            statut=StatutPaiement.SUCCESS,
            numero_telephone=None,
            reference_flutterwave='REF789',
            date_paiement=timezone.now()
        )
        
        # Mock du service SMS qui retourne une erreur de numéro manquant
        mock_sms_service = MagicMock()
        mock_sms_service_class.return_value = mock_sms_service
        mock_sms_service.envoyer_confirmation_paiement.return_value = {
            'success': False,
            'message': 'Aucun numéro de téléphone disponible'
        }
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(paiement_sans_tel)
        
        # Vérifications
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Aucun numéro de téléphone disponible')
    
    @patch('paiements.sms_service.CinetPaySMSService')
    def test_send_sms_with_reference(self, mock_sms_service_class):
        """Test avec référence de paiement"""
        # Mock du service SMS
        mock_sms_service = MagicMock()
        mock_sms_service_class.return_value = mock_sms_service
        mock_sms_service.envoyer_confirmation_paiement.return_value = {
            'success': True,
            'message': 'SMS envoyé avec succès'
        }
        
        # Appeler la fonction
        result = send_payment_confirmation_sms(self.paiement)
        
        # Vérifications
        self.assertTrue(result['success'])
        mock_sms_service.envoyer_confirmation_paiement.assert_called_once_with(self.paiement)
