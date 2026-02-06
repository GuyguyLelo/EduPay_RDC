#!/bin/bash

# Script pour corriger ALLOWED_HOSTS sur Render
echo "🔧 Correction ALLOWED_HOSTS pour Render..."

# Ajouter le domaine exact à ALLOWED_HOSTS
export ALLOWED_HOSTS="localhost,127.0.0.1,testserver,edupay-rdc-p9tw.onrender.com,edupay-rdc.onrender.com,onrender.com"

# Afficher la configuration
echo "✅ ALLOWED_HOSTS configuré avec: $ALLOWED_HOSTS"

# Redémarrer le service
echo "🔄 Redémarrage du service..."
kill -HUP 1
