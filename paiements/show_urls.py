"""
Script pour afficher les URLs de notification, retour et annulation
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from django.conf import settings
from paiements.utils import get_paiement_urls
from paiements.services_cinetpay import CinetPayService

def main():
    """Affiche toutes les URLs pour un paiement"""
    print("=" * 70)
    print("URLs de Configuration CinetPay")
    print("=" * 70)
    print()
    
    # Afficher la configuration actuelle
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    print(f"📍 Site URL configuré: {site_url}")
    print()
    
    # Exemple avec un paiement ID = 1
    paiement_id = 1
    urls = get_paiement_urls(paiement_id)
    
    print("🔗 URLs pour un paiement (exemple avec ID=1):")
    print("-" * 70)
    print(f"✅ URL de retour (Return URL):")
    print(f"   {urls['return_url']}")
    print()
    print(f"📢 URL de notification (Notify URL / Webhook):")
    print(f"   {urls['notify_url']}")
    print()
    print(f"❌ URL d'annulation (Cancel URL):")
    print(f"   {urls['cancel_url']}")
    print()
    
    # Afficher les URLs via le service CinetPay
    try:
        service = CinetPayService()
        service_urls = service.get_all_urls(paiement_id)
        print("=" * 70)
        print("URLs via CinetPayService:")
        print("-" * 70)
        print(f"✅ Return URL: {service_urls['return_url']}")
        print(f"📢 Notify URL: {service_urls['notify_url']}")
        print(f"❌ Cancel URL: {service_urls['cancel_url']}")
    except Exception as e:
        print(f"⚠️  Impossible d'initialiser CinetPayService: {e}")
    
    print()
    print("=" * 70)
    print("📝 Notes importantes:")
    print("-" * 70)
    print("1. En développement local, utilisez un tunnel (ngrok, localtunnel)")
    print("   pour rendre ces URLs accessibles depuis Internet")
    print("2. En production, configurez SITE_URL dans .env avec votre domaine")
    print("3. Configurez ces URLs dans votre interface CinetPay:")
    print("   - Notify URL: pour recevoir les webhooks")
    print("   - Return URL: pour rediriger après paiement réussi")
    print("   - Cancel URL: pour rediriger après annulation")
    print("=" * 70)

if __name__ == '__main__':
    main()


