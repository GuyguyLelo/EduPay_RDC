# Correction Manuelle de la Base de Données Render

## 🚨 Problème Identifié

L'erreur montre que Django essaie de se connecter avec une URL PostgreSQL complète au lieu des paramètres séparés :
```
psycopg2.OperationalError : impossible de traduire le nom d'hôte 
« postgresql://edupay_rdc_vhd4_user:pZeFOQva2rAdUSlzm9K6r8SDxrj0cluW@dpg-d634h47pm1nc73eef1s0-a/edupay_rdc_vhd4 » en adresse
```

## 🔧 Solution Manuelle sur Render

### Étape 1: Accéder au Dashboard Render
1. Connectez-vous à [render.com](https://render.com)
2. Allez dans votre service `edupay-rdc`
3. Cliquez sur "Environment"

### Étape 2: Configurer les Variables d'Environnement

Ajoutez/modifiez ces variables :

```bash
# Configuration Django
DJANGO_SETTINGS_MODULE=EduPay_RDC.settings
DEBUG=False
SECRET_KEY=votre-clé-secrète-générée

# Base de données Render (IMPORTANT)
DB_NAME=edupay_rdc_vhd4
DB_USER=edupay_rdc_vhd4_user
DB_PASSWORD=pZeFOQva2rAdUSlzm9K6r8SDxrj0cluW
DB_HOST=dpg-d634h47pm1nc73eef1s0-a
DB_PORT=5432

# Configuration du site
SITE_URL=https://votre-app.onrender.com
ALLOWED_HOSTS=votre-app.onrender.com,onrender.com

# CinetPay Production
CINETPAY_API_KEY=2069229800671a567b9e80f4.35280533
CINETPAY_SITE_ID=5881999
CINETPAY_ENV=prod

# Superutilisateur
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@edupay-rdc.com
DJANGO_SUPERUSER_PASSWORD=Admin123456!
```

### Étape 3: Variables Render Automatiques

Render fournit automatiquement ces variables. Vous pouvez les utiliser :

```bash
RENDER_DB_HOST=dpg-d634h47pm1nc73eef1s0-a
RENDER_DB_PORT=5432
RENDER_DB_USER=edupay_rdc_vhd4_user
RENDER_DB_PASSWORD=pZeFOQva2rAdUSlzm9K6r8SDxrj0cluW
RENDER_DB_NAME=edupay_rdc_vhd4
RENDER_EXTERNAL_URL=https://votre-app.onrender.com
RENDER_EXTERNAL_HOSTNAME=votre-app.onrender.com
```

### Étape 4: Configuration Alternative avec DATABASE_URL

Si les paramètres séparés ne fonctionnent pas, utilisez DATABASE_URL :

```bash
DATABASE_URL=postgresql://edupay_rdc_vhd4_user:pZeFOQva2rAdUSlzm9K6r8SDxrj0cluW@dpg-d634h47pm1nc73eef1s0-a:5432/edupay_rdc_vhd4
```

## 🔄 Déclencher un Nouveau Déploiement

1. Dans le dashboard Render, allez sur votre service
2. Cliquez sur "Manual Deploy"
3. Choisissez la branche `main`
4. Cliquez sur "Deploy"

## 📊 Vérification du Déploiement

Le build devrait maintenant montrer :
```
🔧 Configuration de la base de données Render...
📊 Configuration DB:
  DB_NAME: edupay_rdc_vhd4
  DB_USER: edupay_rdc_vhd4_user
  DB_HOST: dpg-d634h47pm1nc73eef1s0-a
  DB_PORT: 5432
🗄️ Migration de la base de données PostgreSQL...
✅ Build terminé avec succès!
```

## 🚨 Si l'Erreur Persiste

### Option 1: Utiliser SQLite en Production (Temporaire)

Modifiez temporairement les variables :

```bash
# Forcer SQLite pour tester
USE_SQLITE=True
DB_NAME=db.sqlite3
```

### Option 2: Vérifier les Logs Render

1. Allez dans "Logs" → "edupay-rdc"
2. Cherchez les erreurs de connexion PostgreSQL
3. Vérifiez que les variables sont bien définies

### Option 3: Redémarrer le Service

1. Allez sur votre service
2. Cliquez sur "More" → "Restart Service"

## 🎯 Résultat Attendu

Après correction, l'application devrait :
- ✅ Se connecter à PostgreSQL sans erreur
- ✅ Exécuter les migrations avec succès
- ✅ Démarrer correctement
- ✅ Être accessible sur l'URL Render

## 📞 Support Si Problème Persiste

Si après ces corrections l'erreur persiste :

1. **Vérifiez les variables** : Assurez-vous qu'elles sont exactement comme ci-dessus
2. **Redéployez** : Déclenchez un nouveau déploiement manuel
3. **Contactez le support** : support@render.com

## 🔍 Debug Avancé

Pour vérifier la configuration actuelle :

```bash
# Dans le shell Render
python manage.py shell -c "
from django.conf import settings
print('DB_NAME:', settings.DATABASES['default']['NAME'])
print('DB_USER:', settings.DATABASES['default']['USER'])
print('DB_HOST:', settings.DATABASES['default']['HOST'])
print('DB_PORT:', settings.DATABASES['default']['PORT'])
"
```

Cette configuration manuelle devrait résoudre définitivement le problème de connexion PostgreSQL sur Render.
