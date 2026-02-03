"""
Script pour créer le fichier .env avec les variables CinetPay
"""
import os
from pathlib import Path

# Contenu du fichier .env
env_content = """# Django Settings
SECRET_KEY=django-insecure-^x&feyt3bvm&#+bouop!*iqu%4g3vxr$um^gw@de+&l#-@6-@=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Pour utiliser SQLite (développement uniquement)
USE_SQLITE=True

# Pour utiliser PostgreSQL (recommandé pour la production)
# USE_SQLITE=False
# DB_NAME=edupay_rdc
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# Payment Gateway Configuration
# CinetPay (recommandé pour la RDC)
# IMPORTANT: Remplacez ces valeurs par vos vraies clés CinetPay
# Obtenez-les depuis: https://www.cinetpay.com
# 1. Créez un compte sur https://www.cinetpay.com
# 2. Créez un service marchand
# 3. Récupérez votre API Key et Site ID
CINETPAY_API_KEY=your-cinetpay-api-key-here
CINETPAY_SITE_ID=your-cinetpay-site-id-here
CINETPAY_ENV=test

# Choix de la passerelle de paiement (CINETPAY uniquement)
PAYMENT_GATEWAY=CINETPAY

# Site URL (pour les webhooks et redirections)
# En développement local, utilisez un tunnel (ngrok, localtunnel) pour tester les webhooks
# Exemple avec ngrok: https://abc123.ngrok.io
# En production, utilisez votre domaine réel: https://votre-domaine.com
SITE_URL=http://localhost:8000

# Commission Configuration
COMMISSION_RATE=2.0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@edupay-rdc.com

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
"""

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  Le fichier .env existe déjà.")
        response = input("Voulez-vous le remplacer ? (o/N): ")
        if response.lower() != 'o':
            print("❌ Opération annulée.")
            return
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Fichier .env créé avec succès !")
        print("\n📝 Prochaines étapes :")
        print("1. Éditez le fichier .env et remplacez les valeurs suivantes :")
        print("   - CINETPAY_API_KEY : Votre clé API CinetPay")
        print("   - CINETPAY_SITE_ID : Votre Site ID CinetPay")
        print("   - SITE_URL : Votre URL de production (ou ngrok pour le développement)")
        print("\n2. Obtenez vos clés CinetPay :")
        print("   - Visitez https://www.cinetpay.com")
        print("   - Créez un compte et un service marchand")
        print("   - Récupérez votre API Key et Site ID")
        print("\n3. Configurez le webhook dans CinetPay :")
        print("   - URL : https://votre-domaine.com/api/paiements/webhook/cinetpay/")
        print("   - Consultez GUIDE_WEBHOOK_CINETPAY.md pour plus de détails")
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env : {e}")

if __name__ == '__main__':
    create_env_file()


