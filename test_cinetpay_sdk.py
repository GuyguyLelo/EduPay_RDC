#!/usr/bin/env python3
"""Script pour tester le SDK CinetPay"""
import os
import sys
import django
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("Test SDK CinetPay")
print("=" * 70)

api_key = getattr(settings, 'CINETPAY_API_KEY', '')
site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
environment = getattr(settings, 'CINETPAY_ENV', 'test')

print(f"Environment: {environment}")
print(f"API Key: {api_key[:10]}...")
print(f"Site ID: {site_id}")
print("=" * 70)

try:
    from cinetpay_sdk.s_d_k import Cinetpay
    print("✅ SDK CinetPay importé avec succès")
    
    # Initialiser le client
    client = Cinetpay(api_key, site_id)
    print("✅ Client CinetPay initialisé")
    
    # Tester l'initialisation de paiement
    data = {
        'amount': 100,
        'currency': 'XAF',
        'transaction_id': 'TEST_SDK_123456',
        'description': 'Test paiement SDK',
        'return_url': 'http://localhost:8000',
        'notify_url': 'http://localhost:8000',
        'customer_name': 'Test',
        'customer_surname': 'User',
        'channels': 'ALL',
        'lang': 'fr'
    }
    
    print("\nTest initialisation paiement...")
    response = client.PaymentInitialization(data)
    print(f"Réponse: {response}")
    
    if isinstance(response, dict):
        if response.get('code') == '201' or response.get('status') == 'SUCCESS':
            print("✅ Paiement initialisé avec succès via SDK")
        else:
            print(f"⚠️  Réponse différente attendue: {response}")
    else:
        print(f"⚠️  Réponse non dict: {type(response)}")
        
except ImportError as e:
    print(f"❌ Erreur import SDK: {e}")
except Exception as e:
    print(f"❌ Erreur test SDK: {e}")
    import traceback
    traceback.print_exc()
