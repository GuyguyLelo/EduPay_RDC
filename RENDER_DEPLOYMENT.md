# Guide de Déploiement sur Render - EduPay RDC

## 🚀 Déploiement sur Render

Ce guide explique comment déployer EduPay RDC sur Render avec synchronisation des données PostgreSQL.

### 📋 Prérequis

1. **Compte Render** : Créez un compte sur [render.com](https://render.com)
2. **Dépôt GitHub** : Code poussé sur GitHub
3. **Base de données PostgreSQL locale** : Avec vos données de développement

### 🛠️ Fichiers de Déploiement

#### 1. `build.sh` - Script de build pour Render
- Installation des dépendances
- Migration automatique de la base de données
- Collecte des fichiers statiques
- Création du superutilisateur

#### 2. `render.yaml` - Configuration Render
- Service web Django
- Base de données PostgreSQL
- Variables d'environnement
- Stockage pour les fichiers médias

#### 3. `sync_data.py` - Script de synchronisation
- Export des données locales vers JSON
- Import des données vers la base Render
- Synchronisation bidirectionnelle

#### 4. `migrate_and_sync.sh` - Script complet
- Menu interactif pour la synchronisation
- Détection automatique de l'environnement
- Migration et synchronisation en une seule étape

### 📦 Étapes de Déploiement

#### Étape 1: Préparer le dépôt GitHub

```bash
# Ajouter les fichiers de déploiement
git add build.sh render.yaml sync_data.py migrate_and_sync.sh RENDER_DEPLOYMENT.md
git commit -m "Ajout configuration déploiement Render"
git push origin main
```

#### Étape 2: Créer le service sur Render

1. **Connectez-vous à Render**
2. **Cliquez sur "New +" → "Web Service"**
3. **Connectez votre dépôt GitHub**
4. **Sélectionnez le dépôt EduPay_RDC**
5. **Configurez le service** :
   - **Name** : `edupay-rdc`
   - **Environment** : `Python 3`
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn EduPay_RDC.wsgi:application --workers 3 --bind 0.0.0.0:$PORT`
   - **Health Check Path** : `/admin/`

#### Étape 3: Configurer la base de données

1. **Ajoutez une base de données PostgreSQL** :
   - Cliquez sur "New +" → "PostgreSQL"
   - **Name** : `edupay-rdc-db`
   - **Database Name** : `edupay_rdc`
   - **User** : `edupay_user`

2. **Connectez la base au service web** :
   - Dans les settings du service web
   - Ajoutez la base de données comme dépendance

#### Étape 4: Configurer les variables d'environnement

Ajoutez ces variables dans les settings du service Render :

```bash
# Configuration Django
DJANGO_SETTINGS_MODULE=EduPay_RDC.settings
DEBUG=False
SECRET_KEY=votre-clé-secrète-unique

# Base de données Render
DB_NAME=edupay_rdc
DB_USER=edupay_user
DB_HOST=votre-host-render
DB_PORT=5432
DB_PASSWORD=votre-password-render

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

### 🔄 Synchronisation des Données

#### Option 1: Synchronisation complète (recommandé)

```bash
# En local, exécutez le script interactif
./migrate_and_sync.sh

# Choisissez l'option 3: "Synchronisation complète"
```

#### Option 2: Export puis Import manuel

```bash
# 1. Exporter les données locales
python sync_data.py --export-only

# 2. Transférer les fichiers JSON vers le serveur Render
# (via scp, ou en les pushant dans un dossier temporaire)

# 3. Importer sur Render
python sync_data.py --import-only
```

#### Option 3: Synchronisation directe

```bash
# Configurer les variables d'environnement Render localement
export RENDER_DB_HOST=votre-host-render
export RENDER_DB_USER=edupay_user
export RENDER_DB_PASSWORD=votre-password-render
export RENDER_DB_NAME=edupay_rdc
export RENDER_DB_PORT=5432

# Lancer la synchronisation
python sync_data.py
```

### 📊 Données Synchronisées

Le script synchronise automatiquement :

- ✅ **Utilisateurs** : Comptes utilisateurs et rôles
- ✅ **Établissements** : Informations sur les écoles
- ✅ **Étudiants** : Profils étudiants et inscriptions
- ✅ **Frais** : Configuration des frais scolaires
- ✅ **Paiements** : Historique des paiements (optionnel)

### 🔧 Vérification Post-Déploiement

#### 1. Vérifier le déploiement

```bash
# Test de santé de l'application
curl https://votre-app.onrender.com/admin/

# Vérifier les logs sur Render
# Dashboard → Logs → edupay-rdc
```

#### 2. Tester la synchronisation

```bash
# Vérifier que les données sont bien synchronisées
python manage.py shell
>>> from core.models import User
>>> User.objects.count()
>>> from etablissements.models import Etablissement
>>> Etablissement.objects.count()
```

### 🚨 Dépannage

#### Erreurs communes

1. **Erreur de connexion à la base de données**
   ```bash
   # Vérifier les variables d'environnement
   echo $DB_HOST
   echo $DB_USER
   echo $DB_PASSWORD
   ```

2. **Migration échouée**
   ```bash
   # Forcer la migration
   python manage.py migrate --run-syncdb
   ```

3. **Fichiers statiques non chargés**
   ```bash
   # Recollecter les fichiers statiques
   python manage.py collectstatic --noinput --clear
   ```

4. **Synchronisation échouée**
   ```bash
   # Vérifier la connexion locale et Render
   python sync_data.py --test-connections
   ```

### 📈 Monitoring

#### Logs Render
- **Application Logs** : Dashboard → Logs → edupay-rdc
- **Database Logs** : Dashboard → Logs → edupay-rdc-db
- **Build Logs** : Dashboard → Logs → Build

#### Métriques
- **Response Time** : Temps de réponse moyen
- **Error Rate** : Taux d'erreurs
- **Database Connections** : Connexions à la base de données

### 🔄 Mises à jour

Pour mettre à jour l'application :

1. **Pousser les modifications**
   ```bash
   git add .
   git commit -m "Mise à jour de l'application"
   git push origin main
   ```

2. **Render déploie automatiquement**
   - Le build se lance automatiquement
   - Les migrations sont appliquées
   - L'application est redémarrée

3. **Synchroniser les nouvelles données**
   ```bash
   ./migrate_and_sync.sh
   ```

### 📞 Support Render

- **Documentation** : [render.com/docs](https://render.com/docs)
- **Support** : support@render.com
- **Status** : [status.render.com](https://status.render.com)

### 🎉 Conclusion

Votre application EduPay RDC est maintenant déployée sur Render avec :
- ✅ Base de données PostgreSQL synchronisée
- ✅ Fichiers statiques optimisés
- ✅ Configuration production
- ✅ Monitoring et logs
- ✅ Mises à jour automatiques

Pour toute question technique, consultez le fichier `DEPLOYMENT.md` ou contactez le support technique.
