#!/bin/bash

# EduPay RDC - Build Script for Render
# Ce script gère le déploiement sur Render avec migrations PostgreSQL

set -e  # Arrêter le script en cas d'erreur

echo "🚀 Début du déploiement EduPay RDC sur Render..."

# Variables d'environnement Render
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src
export DJANGO_SETTINGS_MODULE=EduPay_RDC.settings

# Vérifier que nous sommes dans le bon répertoire
cd /opt/render/project/src

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🗄️ Migration de la base de données PostgreSQL..."
python manage.py migrate --noinput

echo "📁 Création des répertoires nécessaires..."
mkdir -p media/uploads
mkdir -p staticfiles
mkdir -p logs

echo "🎨 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🔧 Création du superutilisateur si nécessaire..."
python -c "
from django.contrib.auth import get_user_model
from django.db import transaction
import os

User = get_user_model()

# Vérifier si le superutilisateur existe
if not User.objects.filter(is_superuser=True).exists():
    print('Création du superutilisateur par défaut...')
    try:
        with transaction.atomic():
            User.objects.create_superuser(
                username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
                email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@edupay-rdc.com'),
                password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123456!')
            )
        print('✅ Superutilisateur créé avec succès')
    except Exception as e:
        print(f'⚠️ Erreur lors de la création du superutilisateur: {e}')
        print('   Vous devrez le créer manuellement via python manage.py createsuperuser')
else:
    print('✅ Superutilisateur déjà existant')
"

echo "📊 Vérification de la base de données..."
python manage.py check --deploy

echo "🎯 Configuration des permissions..."
chmod -R 755 media/
chmod -R 755 staticfiles/

echo "✅ Build terminé avec succès!"
echo "🌐 L'application est prête à démarrer sur Render..."

# Script de santé pour Render
echo "🏥 Vérification de santé..."
python manage.py check || exit 1

echo "🎉 Déploiement prêt!"
