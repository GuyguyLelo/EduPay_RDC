#!/bin/bash

# EduPay RDC - Script complet de migration et synchronisation
# Pour déploiement sur Render avec synchronisation des données locales

set -e

echo "🚀 EduPay RDC - Migration et Synchronisation PostgreSQL"
echo "========================================================"

# Vérifier si nous sommes en environnement Render ou local
if [ "$RENDER" = "true" ]; then
    echo "🌐 Environnement Render détecté"
    
    # Migration de la base de données
    echo "📦 Migration de la base de données..."
    python manage.py migrate --noinput
    
    # Collecte des fichiers statiques
    echo "🎨 Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput --clear
    
    # Création du superutilisateur si nécessaire
    echo "👤 Vérification du superutilisateur..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@edupay-rdc.com'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123456!')
    )
    print('✅ Superutilisateur créé')
else:
    print('ℹ️ Superutilisateur déjà existant')
EOF
    
    echo "✅ Configuration Render terminée!"
    
else
    echo "💻 Environnement local détecté"
    
    # Menu interactif
    echo ""
    echo "📋 Options disponibles:"
    echo "1. Exporter les données locales vers des fichiers JSON"
    echo "2. Importer les données depuis les fichiers JSON vers Render"
    echo "3. Synchronisation complète (local → Render)"
    echo "4. Quitter"
    
    read -p "Choisissez une option (1-4): " choice
    
    case $choice in
        1)
            echo "📤 Exportation des données locales..."
            python sync_data.py --export-only
            ;;
        2)
            echo "📥 Importation des données vers Render..."
            python sync_data.py --import-only
            ;;
        3)
            echo "🔄 Synchronisation complète..."
            python sync_data.py
            ;;
        4)
            echo "👋 Au revoir!"
            exit 0
            ;;
        *)
            echo "❌ Option invalide"
            exit 1
            ;;
    esac
fi

echo ""
echo "🎉 Opération terminée avec succès!"
