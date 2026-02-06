#!/usr/bin/env python3
"""
Script de synchronisation des données locales vers la production (Render)
EduPay RDC - Synchronisation PostgreSQL
"""

import os
import sys
import django
import psycopg2
from datetime import datetime
import json

# Configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPay_RDC.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from core.models import User
from etablissements.models import Etablissement
from etudiants.models import Etudiant
from frais.models import Frais
from paiements.models import Paiement

class DatabaseSync:
    def __init__(self):
        self.local_db = settings.DATABASES['default']
        self.render_db = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('RENDER_DB_NAME', 'edupay_rdc'),
            'USER': os.environ.get('RENDER_DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('RENDER_DB_PASSWORD', ''),
            'HOST': os.environ.get('RENDER_DB_HOST', ''),
            'PORT': os.environ.get('RENDER_DB_PORT', '5432'),
        }
        
    def get_connection_string(self, db_config):
        """Générer la chaîne de connexion PostgreSQL"""
        return f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    
    def test_connection(self, db_config):
        """Tester la connexion à la base de données"""
        try:
            conn = psycopg2.connect(
                dbname=db_config['NAME'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                host=db_config['HOST'],
                port=db_config['PORT']
            )
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def export_local_data(self):
        """Exporter les données locales vers des fichiers JSON"""
        print("📤 Exportation des données locales...")
        
        data_dir = 'sync_data'
        os.makedirs(data_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Exporter les utilisateurs
        users = []
        for user in User.objects.all():
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
            }
            users.append(user_data)
        
        with open(f'{data_dir}/users_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Exporter les établissements
        etablissements = []
        for etablissement in Etablissement.objects.all():
            etab_data = {
                'nom': etablissement.nom,
                'description': etablissement.description,
                'adresse': etablissement.adresse,
                'telephone': etablissement.telephone,
                'email': etablissement.email,
                'ville': etablissement.ville,
                'pays': etablissement.pays,
                'type_etablissement': etablissement.type_etablissement,
                'actif': etablissement.actif,
            }
            etablissements.append(etab_data)
        
        with open(f'{data_dir}/etablissements_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(etablissements, f, ensure_ascii=False, indent=2)
        
        # Exporter les étudiants
        etudiants = []
        for etudiant in Etudiant.objects.all():
            etud_data = {
                'user_email': etudiant.user.email,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom,
                'matricule': etudiant.matricule,
                'telephone': etudiant.telephone,
                'date_inscription': etudiant.date_inscription.isoformat(),
                'etablissement_nom': etudiant.etablissement.nom,
            }
            etudiants.append(etud_data)
        
        with open(f'{data_dir}/etudiants_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(etudiants, f, ensure_ascii=False, indent=2)
        
        # Exporter les frais
        frais_list = []
        for frais in Frais.objects.all():
            frais_data = {
                'nom_frais': frais.nom_frais,
                'description': frais.description,
                'montant': float(frais.montant),
                'devise': frais.devise,
                'type_frais': frais.type_frais,
                'echeance': frais.echeance.isoformat() if frais.echeance else None,
                'etablissement_nom': frais.etablissement.nom,
                'actif': frais.actif,
            }
            frais_list.append(frais_data)
        
        with open(f'{data_dir}/frais_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(frais_list, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Données exportées dans le répertoire '{data_dir}'")
        return timestamp
    
    def import_to_render(self, timestamp):
        """Importer les données vers la base de données Render"""
        print("📥 Importation des données vers Render...")
        
        data_dir = 'sync_data'
        
        # Importer les utilisateurs
        with open(f'{data_dir}/users_{timestamp}.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        for user_data in users:
            try:
                user, created = User.objects.get_or_create(
                    email=user_data['email'],
                    defaults={
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'role': user_data['role'],
                        'is_active': user_data['is_active'],
                        'is_staff': user_data['is_staff'],
                        'is_superuser': user_data['is_superuser'],
                        'date_joined': user_data['date_joined'],
                    }
                )
                if created:
                    print(f"✅ Utilisateur créé: {user.email}")
                else:
                    print(f"ℹ️ Utilisateur existant: {user.email}")
            except Exception as e:
                print(f"❌ Erreur lors de l'import de l'utilisateur {user_data['email']}: {e}")
        
        # Importer les établissements
        with open(f'{data_dir}/etablissements_{timestamp}.json', 'r', encoding='utf-8') as f:
            etablissements = json.load(f)
        
        for etab_data in etablissements:
            try:
                etablissement, created = Etablissement.objects.get_or_create(
                    nom=etab_data['nom'],
                    defaults={
                        'description': etab_data['description'],
                        'adresse': etab_data['adresse'],
                        'telephone': etab_data['telephone'],
                        'email': etab_data['email'],
                        'ville': etab_data['ville'],
                        'pays': etab_data['pays'],
                        'type_etablissement': etab_data['type_etablissement'],
                        'actif': etab_data['actif'],
                    }
                )
                if created:
                    print(f"✅ Établissement créé: {etablissement.nom}")
                else:
                    print(f"ℹ️ Établissement existant: {etablissement.nom}")
            except Exception as e:
                print(f"❌ Erreur lors de l'import de l'établissement {etab_data['nom']}: {e}")
        
        # Importer les étudiants
        with open(f'{data_dir}/etudiants_{timestamp}.json', 'r', encoding='utf-8') as f:
            etudiants = json.load(f)
        
        for etud_data in etudiants:
            try:
                user = User.objects.get(email=etud_data['user_email'])
                etablissement = Etablissement.objects.get(nom=etud_data['etablissement_nom'])
                
                etudiant, created = Etudiant.objects.get_or_create(
                    user=user,
                    defaults={
                        'nom': etud_data['nom'],
                        'prenom': etud_data['prenom'],
                        'matricule': etud_data['matricule'],
                        'telephone': etud_data['telephone'],
                        'date_inscription': etud_data['date_inscription'],
                        'etablissement': etablissement,
                    }
                )
                if created:
                    print(f"✅ Étudiant créé: {etudiant.nom} {etudiant.prenom}")
                else:
                    print(f"ℹ️ Étudiant existant: {etudiant.nom} {etudiant.prenom}")
            except Exception as e:
                print(f"❌ Erreur lors de l'import de l'étudiant {etud_data['user_email']}: {e}")
        
        # Importer les frais
        with open(f'{data_dir}/frais_{timestamp}.json', 'r', encoding='utf-8') as f:
            frais_list = json.load(f)
        
        for frais_data in frais_list:
            try:
                etablissement = Etablissement.objects.get(nom=frais_data['etablissement_nom'])
                
                frais, created = Frais.objects.get_or_create(
                    nom_frais=frais_data['nom_frais'],
                    etablissement=etablissement,
                    defaults={
                        'description': frais_data['description'],
                        'montant': frais_data['montant'],
                        'devise': frais_data['devise'],
                        'type_frais': frais_data['type_frais'],
                        'echeance': datetime.fromisoformat(frais_data['echeance']) if frais_data['echeance'] else None,
                        'actif': frais_data['actif'],
                    }
                )
                if created:
                    print(f"✅ Frais créé: {frais.nom_frais}")
                else:
                    print(f"ℹ️ Frais existant: {frais.nom_frais}")
            except Exception as e:
                print(f"❌ Erreur lors de l'import des frais {frais_data['nom_frais']}: {e}")
        
        print("✅ Importation des données terminée!")
    
    def sync_full(self):
        """Synchronisation complète"""
        print("🔄 Début de la synchronisation complète...")
        
        # Test des connexions
        print("🔍 Test des connexions aux bases de données...")
        
        if not self.test_connection(self.local_db):
            print("❌ Impossible de se connecter à la base locale")
            return False
        
        if not self.test_connection(self.render_db):
            print("❌ Impossible de se connecter à la base de données Render")
            print("   Vérifiez les variables d'environnement RENDER_DB_*")
            return False
        
        # Exporter les données locales
        timestamp = self.export_local_data()
        
        # Importer vers Render
        self.import_to_render(timestamp)
        
        print("🎉 Synchronisation terminée avec succès!")
        return True

def main():
    """Fonction principale"""
    print("🚀 EduPay RDC - Synchronisation PostgreSQL")
    print("=" * 50)
    
    sync = DatabaseSync()
    
    # Menu interactif
    while True:
        print("\n📋 Options:")
        print("1. Synchronisation complète (local → Render)")
        print("2. Exporter uniquement les données locales")
        print("3. Importer uniquement les données vers Render")
        print("4. Tester les connexions")
        print("5. Quitter")
        
        choice = input("\nChoisissez une option (1-5): ")
        
        if choice == '1':
            sync.sync_full()
        elif choice == '2':
            sync.export_local_data()
        elif choice == '3':
            timestamp = input("Entrez le timestamp des données à importer (ex: 20240206_123456): ")
            sync.import_to_render(timestamp)
        elif choice == '4':
            print("🔍 Test de connexion locale...")
            if sync.test_connection(sync.local_db):
                print("✅ Connexion locale réussie")
            else:
                print("❌ Connexion locale échouée")
            
            print("🔍 Test de connexion Render...")
            if sync.test_connection(sync.render_db):
                print("✅ Connexion Render réussie")
            else:
                print("❌ Connexion Render échouée")
        elif choice == '5':
            print("👋 Au revoir!")
            break
        else:
            print("❌ Option invalide. Veuillez réessayer.")

if __name__ == '__main__':
    main()
