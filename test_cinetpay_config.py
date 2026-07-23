#!/usr/bin/env python3
"""Script pour tester la configuration CinetPay"""
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
print("Configuration CinetPay")
print("=" * 70)
print(f"CINETPAY_API_KEY: {getattr(settings, 'CINETPAY_API_KEY', '')[:10]}..." if getattr(settings, 'CINETPAY_API_KEY', '') else "CINETPAY_API_KEY: Non défini")
print(f"CINETPAY_SITE_ID: {getattr(settings, 'CINETPAY_SITE_ID', 'Non défini')}")
print(f"CINETPAY_ENV: {getattr(settings, 'CINETPAY_ENV', 'Non défini')}")
print(f"DEBUG: {getattr(settings, 'DEBUG', 'Non défini')}")
print("=" * 70)

# Tester le service CinetPay
try:
    from paiements.services_cinetpay import CinetPayService
    service = CinetPayService()
    print(f"✅ Service CinetPay initialisé avec succès")
    print(f"   Base URL: {service.base_url}")
    print(f"   Checkout URL: {service.checkout_url}")
except Exception as e:
    print(f"❌ Erreur d'initialisation CinetPay: {e}")
    sys.exit(1)

# Tester un endpoint simple
import requests
print("\nTest de connexion à l'API CinetPay...")
try:
    response = requests.get(service.base_url.replace('/v1', ''), timeout=10)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ API CinetPay accessible")
    else:
        print(f"   ⚠️  API CinetPay répond mais avec un code différent")
except Exception as e:
    print(f"   ❌ Erreur de connexion: {e}")
