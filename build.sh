#!/bin/bash

# EduPay RDC - Build Script for Render
# Ce script gère le déploiement sur Render avec fallback SQLite

set -e  # Arrêter le script en cas d'erreur

echo "🚀 Début du déploiement EduPay RDC sur Render..."

# Variables d'environnement Render
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src
export DJANGO_SETTINGS_MODULE=EduPay_RDC.settings

# Vérifier que nous sommes dans le bon répertoire
cd /opt/render/project/src

# Forcer Python 3.11 si disponible
if command -v python3.11 &> /dev/null; then
    echo "🐍 Utilisation de Python 3.11"
    export PATH="/opt/render/project/src/.venv/bin:$PATH"
    python3.11 -m pip install --upgrade pip
    python3.11 -m pip install -r requirements.txt
    python3.11 -m pip install psycopg2-binary==2.9.9
    PYTHON_CMD="python3.11"
else
    echo "🐍 Utilisation de Python par défaut"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install psycopg2-binary==2.9.9
    PYTHON_CMD="python"
fi

echo "📊 Configuration de la base de données..."
echo "  Mode: SQLite (temporaire - PostgreSQL en cours de configuration)"
echo "  Python: $($PYTHON_CMD --version)"

echo "🗄️ Migration de la base de données..."
$PYTHON_CMD manage.py migrate --noinput

echo "📁 Création des répertoires nécessaires..."
mkdir -p media/uploads
mkdir -p staticfiles
mkdir -p logs

echo "🎨 Collecte des fichiers statiques..."
$PYTHON_CMD manage.py collectstatic --noinput --clear

echo "🔧 Création du superutilisateur si nécessaire..."
# Retarder la création du superutilisateur après les migrations et collectstatic
$PYTHON_CMD manage.py shell << 'EOF'
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
EOF

echo "📊 Vérification de la base de données..."
$PYTHON_CMD manage.py check --deploy

echo "🔧 Configuration des permissions..."
chmod -R 755 media/
chmod -R 755 staticfiles/

echo "✅ Build terminé avec succès!"
echo "🌐 L'application est prête à démarrer sur Render..."
echo "💡 Note: Utilisation temporaire de SQLite. PostgreSQL sera configuré ultérieurement."

# Script de santé pour Render
echo "🏥 Vérification de santé..."
$PYTHON_CMD manage.py check || exit 1

echo "🎉 Déploiement prêt!"
