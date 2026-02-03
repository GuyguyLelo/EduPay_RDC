"""
Script pour créer des données de test pour EduPay RDC
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from decimal import Decimal
from core.models import User, UserRole
from etablissements.models import Etablissement, TypeEtablissement, StatutEtablissement, ComptePaiement, OperateurMobileMoney
from etudiants.models import Etudiant
from frais.models import Frais, Devise

def create_test_data():
    """Crée des données de test"""
    print("=" * 60)
    print("Création des données de test pour EduPay RDC")
    print("=" * 60)
    
    # 1. Créer un établissement admin
    print("\n1. Création d'un administrateur d'établissement...")
    admin_email = "admin.etab@test.com"
    admin_password = "admin123"
    
    if User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.get(email=admin_email)
        print(f"   ✓ Administrateur existant: {admin_email}")
    else:
        admin_user = User.objects.create_user(
            email=admin_email,
            password=admin_password,
            role=UserRole.ETABLISSEMENT_ADMIN
        )
        print(f"   ✓ Administrateur créé: {admin_email} / {admin_password}")
    
    # 2. Créer un établissement
    print("\n2. Création d'un établissement...")
    etablissement, created = Etablissement.objects.get_or_create(
        nom="Université de Test",
        defaults={
            'type': TypeEtablissement.UNIVERSITE,
            'email': 'contact@univ-test.cd',
            'telephone': '+243900000001',
            'adresse': 'Kinshasa, RDC',
            'statut': StatutEtablissement.ACTIF,
            'admin': admin_user
        }
    )
    if created:
        print(f"   ✓ Établissement créé: {etablissement.nom}")
    else:
        print(f"   ✓ Établissement existant: {etablissement.nom}")
        etablissement.admin = admin_user
        etablissement.statut = StatutEtablissement.ACTIF
        etablissement.save()
    
    # 3. Créer un compte Mobile Money
    print("\n3. Création d'un compte Mobile Money...")
    compte, created = ComptePaiement.objects.get_or_create(
        etablissement=etablissement,
        operateur=OperateurMobileMoney.MPESA,
        defaults={
            'intitule': 'Compte principal M-Pesa',
            'numero_compte': '+243900000001',
            'actif': True
        }
    )
    if created:
        print(f"   ✓ Compte Mobile Money créé: {compte.get_operateur_display()}")
    else:
        print(f"   ✓ Compte Mobile Money existant: {compte.get_operateur_display()}")
    
    # 4. Créer des étudiants
    print("\n4. Création d'étudiants de test...")
    etudiants_data = [
        {
            'email': 'etudiant1@test.com',
            'password': 'etudiant123',
            'nom': 'Kabila',
            'prenom': 'Jean',
            'matricule': 'ETU2024001',
            'telephone': '+243900000010'
        },
        {
            'email': 'etudiant2@test.com',
            'password': 'etudiant123',
            'nom': 'Mukendi',
            'prenom': 'Marie',
            'matricule': 'ETU2024002',
            'telephone': '+243900000011'
        },
        {
            'email': 'etudiant3@test.com',
            'password': 'etudiant123',
            'nom': 'Tshisekedi',
            'prenom': 'Paul',
            'matricule': 'ETU2024003',
            'telephone': '+243900000012'
        }
    ]
    
    for etud_data in etudiants_data:
        if User.objects.filter(email=etud_data['email']).exists():
            user = User.objects.get(email=etud_data['email'])
            etudiant, created = Etudiant.objects.get_or_create(
                user=user,
                defaults={
                    'nom': etud_data['nom'],
                    'prenom': etud_data['prenom'],
                    'matricule': etud_data['matricule'],
                    'etablissement': etablissement,
                    'telephone': etud_data['telephone']
                }
            )
            if not created:
                print(f"   ✓ Étudiant existant: {etudiant.nom_complet} ({etud_data['email']})")
            else:
                print(f"   ✓ Étudiant créé: {etudiant.nom_complet} ({etud_data['email']})")
        else:
            user = User.objects.create_user(
                email=etud_data['email'],
                password=etud_data['password'],
                role=UserRole.ETUDIANT
            )
            etudiant = Etudiant.objects.create(
                user=user,
                nom=etud_data['nom'],
                prenom=etud_data['prenom'],
                matricule=etud_data['matricule'],
                etablissement=etablissement,
                telephone=etud_data['telephone']
            )
            print(f"   ✓ Étudiant créé: {etudiant.nom_complet} ({etud_data['email']} / {etud_data['password']})")
    
    # 5. Créer des frais
    print("\n5. Création de frais scolaires...")
    frais_data = [
        {
            'nom_frais': 'Frais de scolarité',
            'montant': Decimal('50000.00'),
            'devise': Devise.CDF,
            'annee_academique': '2024-2025',
            'description': 'Frais de scolarité pour l\'année académique 2024-2025'
        },
        {
            'nom_frais': 'Frais d\'inscription',
            'montant': Decimal('25000.00'),
            'devise': Devise.CDF,
            'annee_academique': '2024-2025',
            'description': 'Frais d\'inscription pour nouveaux étudiants'
        },
        {
            'nom_frais': 'Frais de bibliothèque',
            'montant': Decimal('10000.00'),
            'devise': Devise.CDF,
            'annee_academique': '2024-2025',
            'description': 'Accès à la bibliothèque pour l\'année'
        }
    ]
    
    for frais_info in frais_data:
        frais, created = Frais.objects.get_or_create(
            etablissement=etablissement,
            nom_frais=frais_info['nom_frais'],
            defaults=frais_info
        )
        if created:
            print(f"   ✓ Frais créé: {frais.nom_frais} - {frais.montant} {frais.devise}")
        else:
            print(f"   ✓ Frais existant: {frais.nom_frais} - {frais.montant} {frais.devise}")
    
    print("\n" + "=" * 60)
    print("✅ Données de test créées avec succès !")
    print("=" * 60)
    print("\n📋 Récapitulatif des identifiants de test :")
    print("\n🔑 Super Admin (si créé):")
    print("   Email: admin@edupay-rdc.com")
    print("   Mot de passe: admin123")
    print("\n🏫 Administrateur d'établissement:")
    print(f"   Email: {admin_email}")
    print(f"   Mot de passe: {admin_password}")
    print("\n👨‍🎓 Étudiants:")
    for etud_data in etudiants_data:
        print(f"   - {etud_data['nom']} {etud_data['prenom']}: {etud_data['email']} / {etud_data['password']}")
    print("\n💡 Pour tester les paiements:")
    print("   1. Connectez-vous en tant qu'étudiant")
    print("   2. Allez sur votre tableau de bord")
    print("   3. Cliquez sur 'Payer' pour un frais")
    print("   4. Choisissez votre méthode de paiement (QR Code, Carte, Mobile Money)")
    print("\n⚠️  Note: Les paiements nécessitent des clés CinetPay configurées dans .env")
    print("=" * 60)

if __name__ == '__main__':
    create_test_data()


