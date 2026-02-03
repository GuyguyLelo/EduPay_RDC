"""
Script de diagnostic pour vérifier la configuration SMS
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from django.conf import settings
from paiements.models import Paiement
from paiements.sms_service import CinetPaySMSService
from paiements.receipts import send_payment_confirmation_sms

def diagnostic_sms():
    """Diagnostic complet de la configuration SMS"""
    print("=" * 60)
    print("DIAGNOSTIC SMS - Configuration CinetPay SMS")
    print("=" * 60)
    print()
    
    # 1. Vérifier les variables d'environnement
    print("1. Vérification des variables d'environnement:")
    print("-" * 60)
    
    api_key = getattr(settings, 'CINETPAY_SMS_API_KEY', '')
    sender_id = getattr(settings, 'CINETPAY_SMS_SENDER_ID', 'EDUPAY')
    
    if api_key:
        print(f"✅ CINETPAY_SMS_API_KEY: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
    else:
        print("❌ CINETPAY_SMS_API_KEY: NON CONFIGURÉ")
        print("   → Ajoutez CINETPAY_SMS_API_KEY dans votre fichier .env")
        print("   → Contactez support@cinetpay.com pour obtenir une clé API SMS")
    
    print(f"✅ CINETPAY_SMS_SENDER_ID: {sender_id}")
    print()
    
    # 2. Tester l'initialisation du service SMS
    print("2. Test d'initialisation du service SMS:")
    print("-" * 60)
    try:
        sms_service = CinetPaySMSService()
        print("✅ Service SMS initialisé avec succès")
    except ValueError as e:
        print(f"❌ Erreur d'initialisation: {str(e)}")
        print()
        print("SOLUTION:")
        print("   1. Ajoutez CINETPAY_SMS_API_KEY dans votre fichier .env")
        print("   2. Redémarrez le serveur Django")
        return
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return
    print()
    
    # 3. Vérifier les paiements récents
    print("3. Vérification des paiements récents:")
    print("-" * 60)
    paiements_reussis = Paiement.objects.filter(
        statut='SUCCESS'
    ).order_by('-date_paiement')[:5]
    
    if not paiements_reussis.exists():
        print("⚠️  Aucun paiement réussi trouvé")
        print("   → Le SMS n'est envoyé qu'après un paiement réussi")
    else:
        print(f"✅ {paiements_reussis.count()} paiement(s) réussi(s) trouvé(s)")
        print()
        
        for paiement in paiements_reussis:
            print(f"   Paiement #{paiement.id}:")
            print(f"   - Montant: {paiement.montant} {paiement.devise}")
            print(f"   - Date: {paiement.date_paiement}")
            print(f"   - Numéro téléphone: {paiement.numero_telephone or 'NON DÉFINI'}")
            
            if not paiement.numero_telephone:
                print("   ⚠️  ATTENTION: Aucun numéro de téléphone dans le paiement")
                if hasattr(paiement.etudiant, 'telephone'):
                    print(f"   → Numéro de l'étudiant: {paiement.etudiant.telephone}")
            print()
    print()
    
    # 4. Test d'envoi SMS (si un paiement existe)
    print("4. Test d'envoi SMS (sur le dernier paiement réussi):")
    print("-" * 60)
    if paiements_reussis.exists():
        dernier_paiement = paiements_reussis.first()
        
        if dernier_paiement.numero_telephone or (hasattr(dernier_paiement.etudiant, 'telephone') and dernier_paiement.etudiant.telephone):
            print(f"   Test sur le paiement #{dernier_paiement.id}")
            print(f"   Numéro: {dernier_paiement.numero_telephone or dernier_paiement.etudiant.telephone}")
            print()
            
            reponse = input("   Voulez-vous envoyer un SMS de test ? (o/N): ")
            if reponse.lower() == 'o':
                result = send_payment_confirmation_sms(dernier_paiement)
                if result.get('success'):
                    print("   ✅ SMS envoyé avec succès !")
                else:
                    print(f"   ❌ Échec: {result.get('message')}")
            else:
                print("   Test annulé")
        else:
            print("   ⚠️  Aucun numéro de téléphone disponible pour tester")
    else:
        print("   ⚠️  Aucun paiement réussi pour tester")
    print()
    
    # 5. Vérifier les logs
    print("5. Vérification des logs:")
    print("-" * 60)
    print("   Consultez les logs Django pour voir les erreurs SMS:")
    print("   - Cherchez les lignes contenant 'SMS' ou 'CinetPaySMSService'")
    print("   - Les erreurs sont loggées avec logger.warning() ou logger.error()")
    print()
    
    # 6. Résumé et recommandations
    print("=" * 60)
    print("RÉSUMÉ ET RECOMMANDATIONS")
    print("=" * 60)
    print()
    
    if not api_key:
        print("❌ PROBLÈME PRINCIPAL: Clé API SMS non configurée")
        print()
        print("ÉTAPES À SUIVRE:")
        print("1. Contactez support@cinetpay.com pour obtenir une clé API SMS")
        print("2. Ajoutez dans votre fichier .env:")
        print("   CINETPAY_SMS_API_KEY=votre-cle-api-ici")
        print("   CINETPAY_SMS_SENDER_ID=EDUPAY")
        print("3. Redémarrez le serveur Django")
    else:
        print("✅ Configuration SMS présente")
        print()
        print("VÉRIFICATIONS À FAIRE:")
        print("1. Vérifiez que le numéro de téléphone est correct dans le paiement")
        print("2. Vérifiez les logs Django pour les erreurs d'envoi")
        print("3. Vérifiez que le paiement a bien le statut SUCCESS")
        print("4. Contactez CinetPay si le problème persiste")
    print()

if __name__ == '__main__':
    diagnostic_sms()




