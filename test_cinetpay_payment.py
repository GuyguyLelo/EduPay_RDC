#!/usr/bin/env python3
"""Script pour tester l'endpoint d'initialisation de paiement CinetPay"""
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
import requests
import json

print("=" * 70)
print("Test endpoint initialisation paiement CinetPay")
print("=" * 70)

api_key = getattr(settings, 'CINETPAY_API_KEY', '')
site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
environment = getattr(settings, 'CINETPAY_ENV', 'test')

# Nouveaux domaines selon le SDK JavaScript 2024
if environment == 'prod':
    checkout_url = 'https://api.cinetpay.co'
else:
    checkout_url = 'https://api.cinetpay.net'

print(f"Environment: {environment}")
print(f"Checkout URL: {checkout_url}")
print(f"API Key: {api_key[:10]}...")
print(f"Site ID: {site_id}")
print("=" * 70)

# Tester différents endpoints possibles selon la nouvelle API CinetPay
endpoints = [
    f"{checkout_url}/payment",
    f"{checkout_url}/payment/initialize",
    f"{checkout_url}/v2/payment",
    f"{checkout_url}/api/payment",
    f"{checkout_url}/checkout/payment",
]

for endpoint in endpoints:
    print(f"\nTest endpoint: {endpoint}")
    
    data = {
        'apikey': api_key,
        'site_id': site_id,
        'amount': 100,
        'currency': 'XAF',
        'transaction_id': 'TEST_123456',
        'description': 'Test paiement',
        'return_url': 'http://localhost:8000',
        'notify_url': 'http://localhost:8000',
        'customer_name': 'Test',
        'customer_surname': 'User',
    }
    
    try:
        response = requests.post(
            endpoint,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Succès!")
            print(f"  Réponse: {json.dumps(result, indent=2)}")
            break
        else:
            print(f"  ⚠️  Échec")
            print(f"  Réponse: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
