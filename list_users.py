"""
Script pour lister les utilisateurs et réinitialiser les mots de passe
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from core.models import User, UserRole


def list_users():
    """Liste tous les utilisateurs"""
    print("=" * 70)
    print("📋 LISTE DES UTILISATEURS")
    print("=" * 70)
    print()
    
    users = User.objects.all().order_by('email')
    
    if not users.exists():
        print("❌ Aucun utilisateur trouvé dans la base de données.")
        return
    
    print(f"Total d'utilisateurs: {users.count()}\n")
    print(f"{'ID':<5} {'Email':<40} {'Rôle':<20} {'Actif':<8} {'Staff':<8} {'Superuser':<10}")
    print("-" * 70)
    
    for user in users:
        role_display = user.get_role_display() if hasattr(user, 'get_role_display') else user.role
        active = "✅" if user.is_active else "❌"
        staff = "✅" if user.is_staff else "❌"
        superuser = "✅" if user.is_superuser else "❌"
        
        print(f"{user.id:<5} {user.email:<40} {role_display:<20} {active:<8} {staff:<8} {superuser:<10}")
    
    print()
    print("=" * 70)


def reset_password(email=None, new_password=None):
    """Réinitialise le mot de passe d'un utilisateur"""
    if not email:
        print("❌ Veuillez fournir un email.")
        return False
    
    try:
        user = User.objects.get(email=email)
        
        if not new_password:
            # Générer un mot de passe par défaut
            import secrets
            new_password = secrets.token_urlsafe(12)
        
        user.set_password(new_password)
        user.save()
        
        print("=" * 70)
        print("✅ MOT DE PASSE RÉINITIALISÉ AVEC SUCCÈS")
        print("=" * 70)
        print(f"📧 Email: {user.email}")
        print(f"🔑 Nouveau mot de passe: {new_password}")
        print(f"👤 Rôle: {user.get_role_display() if hasattr(user, 'get_role_display') else user.role}")
        print()
        print("⚠️  IMPORTANT: Changez ce mot de passe après la première connexion!")
        print("=" * 70)
        
        return True
    except User.DoesNotExist:
        print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        return False


def create_admin_user():
    """Crée ou réinitialise un utilisateur admin par défaut"""
    email = 'admin@edupay-rdc.com'
    password = 'admin123'
    
    try:
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.set_password(password)
            user.role = UserRole.SUPER_ADMIN
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print(f"✅ Utilisateur admin mis à jour!")
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
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_users()
        
        elif command == 'reset':
            if len(sys.argv) < 3:
                print("Usage: python list_users.py reset <email> [nouveau_mot_de_passe]")
                print("Exemple: python list_users.py reset admin@edupay-rdc.com")
                print("Exemple: python list_users.py reset admin@edupay-rdc.com MonNouveauMotDePasse123")
                return
            
            email = sys.argv[2]
            new_password = sys.argv[3] if len(sys.argv) > 3 else None
            reset_password(email, new_password)
        
        elif command == 'create-admin':
            create_admin_user()
        
        else:
            print("Commandes disponibles:")
            print("  list          - Liste tous les utilisateurs")
            print("  reset <email> [password] - Réinitialise le mot de passe")
            print("  create-admin  - Crée/réinitialise l'utilisateur admin par défaut")
    else:
        # Par défaut, lister les utilisateurs
        list_users()
        print()
        print("💡 Commandes disponibles:")
        print("  python list_users.py list          - Liste tous les utilisateurs")
        print("  python list_users.py reset <email> [password] - Réinitialise le mot de passe")
        print("  python list_users.py create-admin - Crée/réinitialise l'admin par défaut")


if __name__ == '__main__':
    main()
