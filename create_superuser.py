"""
Script pour créer un super utilisateur de manière non-interactive
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from core.models import User, UserRole

# Créer le super utilisateur
email = 'admin@edupay-rdc.com'
password = 'admin123'  # À changer en production !

try:
    if User.objects.filter(email=email).exists():
        print(f"L'utilisateur {email} existe déjà.")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.role = UserRole.SUPER_ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        print(f"✅ Mot de passe mis à jour pour {email}")
    else:
        user = User.objects.create_superuser(
            email=email,
            password=password,
            role=UserRole.SUPER_ADMIN
        )
        print(f"✅ Super utilisateur créé avec succès!")
        print(f"📧 Email: {email}")
        print(f"🔑 Mot de passe: {password}")
        print("\n⚠️  IMPORTANT: Changez le mot de passe après la première connexion!")
except Exception as e:
    print(f"❌ Erreur lors de la création du super utilisateur: {e}")
    sys.exit(1)

