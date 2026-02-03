# EduPay RDC - Plateforme de Paiement des Frais Scolaires

Plateforme SaaS complète pour la gestion et le paiement en ligne des frais scolaires en République Démocratique du Congo (RDC).

## 📋 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture Technique](#architecture-technique)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Déploiement](#déploiement)
- [Tests](#tests)
- [Contributeurs](#contributeurs)

## 🎯 Description

EduPay RDC est une plateforme web permettant aux établissements scolaires (écoles, instituts supérieurs, universités) de gérer leurs frais scolaires et aux étudiants de payer en ligne via Mobile Money (M-Pesa, Orange Money, Airtel Money).

### Rôles dans le système

- **SUPER_ADMIN** : Gestion globale de la plateforme, tous les établissements et transactions
- **ETABLISSEMENT_ADMIN** : Gestion de son établissement (frais, étudiants, paiements)
- **ETUDIANT** : Consultation et paiement de ses frais scolaires

## ✨ Fonctionnalités

### Pour les établissements
- ✅ Configuration des frais scolaires (montants, devises CDF/USD)
- ✅ Gestion des comptes Mobile Money (M-Pesa, Orange Money, Airtel Money)
- ✅ Suivi des paiements des étudiants
- ✅ Génération de rapports financiers
- ✅ Gestion des étudiants

### Pour les étudiants
- ✅ Consultation des frais à payer
- ✅ Paiement en ligne via Mobile Money
- ✅ Reçus PDF automatiques
- ✅ Notifications par email

### Pour la plateforme (Super Admin)
- ✅ Dashboard complet avec statistiques
- ✅ Gestion des établissements (activation/suspension)
- ✅ Suivi des revenus et commissions
- ✅ Rapports mensuels détaillés
- ✅ Gestion des abonnements

## 🏗️ Architecture Technique

### Stack Technologique

- **Backend** : Django 5.2+
- **API** : Django Rest Framework
- **Authentification** : JWT (Simple JWT)
- **Base de données** : PostgreSQL (SQLite en développement)
- **Paiement** : CinetPay (Mobile Money RDC)
- **PDF** : ReportLab
- **Docker** : Prêt pour containerisation

### Structure du Projet

```
EduPay_RDC/
├── core/                    # Utilisateurs & authentification
├── etablissements/          # Gestion des établissements
├── etudiants/              # Gestion des étudiants
├── frais/                  # Frais scolaires
├── paiements/              # Transactions & webhooks
├── abonnements/            # Facturation des établissements
├── dashboard_admin/        # Dashboard super admin
└── EduPay_RDC/            # Configuration du projet
```

## 🚀 Installation

### Prérequis

- Python 3.10+
- PostgreSQL 12+ (ou SQLite pour le développement)
- pip
- virtualenv (recommandé)

### Installation locale

1. **Cloner le projet**
```bash
git clone <repository-url>
cd EduPay_RDC
```

2. **Créer et activer un environnement virtuel**
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
# Copier le fichier d'exemple
cp env.example .env

# Éditer .env avec vos configurations
```

5. **Configurer la base de données**

**Option 1 : PostgreSQL (recommandé)**
```bash
# Créer la base de données PostgreSQL
createdb edupay_rdc

# Dans .env, configurer :
USE_SQLITE=False
DB_NAME=edupay_rdc
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

**Option 2 : SQLite (développement)**
```bash
# Dans .env :
USE_SQLITE=True
```

6. **Exécuter les migrations**
```bash
python manage.py migrate
```

7. **Créer un super utilisateur**
```bash
python manage.py createsuperuser
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

Le serveur sera accessible sur `http://localhost:8000`

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Django Settings
SECRET_KEY=votre-secret-key-securise
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_SQLITE=False
DB_NAME=edupay_rdc
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CinetPay (recommandé pour la RDC)
CINETPAY_API_KEY=votre-cinetpay-api-key
CINETPAY_SITE_ID=votre-cinetpay-site-id
CINETPAY_ENV=test  # ou 'prod' pour la production

# Commission
COMMISSION_RATE=2.0  # 2% par défaut

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=noreply@edupay-rdc.com
```

### Configuration CinetPay

1. Créer un compte sur [CinetPay](https://www.cinetpay.com)
2. Créer un service marchand
3. Obtenir votre API Key et Site ID
4. Configurer le webhook : `https://votre-domaine.com/api/paiements/webhook/cinetpay/`
5. Ajouter les clés dans le fichier `.env`

## 📖 Utilisation

### Créer un établissement

1. Se connecter en tant que SUPER_ADMIN
2. Via l'admin Django ou l'API, créer un établissement
3. Assigner un administrateur à l'établissement
4. Activer l'établissement

### Configurer les frais scolaires

1. Se connecter en tant que ETABLISSEMENT_ADMIN
2. Créer les différents types de frais (inscription, scolarité, etc.)
3. Définir les montants et devises

### Effectuer un paiement

1. L'étudiant se connecte
2. Consulte ses frais à payer
3. Initie un paiement avec son numéro Mobile Money
4. Confirme le paiement sur son téléphone
5. Reçoit un reçu PDF par email

## 📡 API Documentation

### Authentification

Toutes les requêtes API (sauf inscription/connexion) nécessitent un token JWT dans le header :
```
Authorization: Bearer <access_token>
```

### Endpoints principaux

#### Authentification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `GET /api/auth/profile/` - Profil utilisateur

#### Établissements
- `GET /api/etablissements/` - Liste des établissements
- `POST /api/etablissements/` - Créer un établissement
- `GET /api/etablissements/{id}/` - Détails d'un établissement

#### Étudiants
- `GET /api/etudiants/` - Liste des étudiants
- `POST /api/etudiants/` - Créer un étudiant
- `GET /api/etudiants/{id}/` - Détails d'un étudiant

#### Frais
- `GET /api/frais/` - Liste des frais
- `POST /api/frais/` - Créer des frais
- `GET /api/frais/{id}/` - Détails d'un frais

#### Paiements
- `GET /api/paiements/paiements/` - Liste des paiements
- `POST /api/paiements/paiements/` - Créer un paiement
- `GET /api/paiements/paiements/{id}/` - Détails d'un paiement
- `POST /api/paiements/paiements/{id}/verifier/` - Vérifier un paiement
- `POST /api/paiements/webhook/cinetpay/` - Webhook CinetPay

#### Dashboard Admin
- `GET /api/dashboard/overview/` - Vue d'ensemble
- `GET /api/dashboard/etablissements/` - Liste des établissements
- `POST /api/dashboard/etablissements/{id}/activer/` - Activer un établissement
- `POST /api/dashboard/etablissements/{id}/suspendre/` - Suspendre un établissement
- `GET /api/dashboard/paiements/` - Liste des paiements
- `GET /api/dashboard/rapports/mensuels/` - Rapports mensuels

### Exemple de requête

```bash
# Connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "etudiant@example.com", "password": "password123"}'

# Créer un paiement
curl -X POST http://localhost:8000/api/paiements/paiements/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "etudiant": 1,
    "frais": 1,
    "numero_telephone": "+243900000000",
    "operateur": "MPESA"
  }'
```

## 🐳 Déploiement avec Docker

### Utilisation de Docker Compose

1. **Construire et lancer les conteneurs**
```bash
docker-compose up -d --build
```

2. **Exécuter les migrations**
```bash
docker-compose exec web python manage.py migrate
```

3. **Créer un super utilisateur**
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Collecter les fichiers statiques**
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Configuration de production

1. Modifier `DEBUG=False` dans `.env`
2. Configurer `ALLOWED_HOSTS` avec votre domaine
3. Utiliser PostgreSQL en production
4. Configurer HTTPS (obligatoire)
5. Utiliser les clés CinetPay en mode `prod`
6. Configurer un serveur web (Nginx + Gunicorn)

## 🧪 Tests

Exécuter les tests unitaires :

```bash
python manage.py test
```

Tests par app :

```bash
python manage.py test core
python manage.py test paiements
```

## 📊 Structure de la Base de Données

### Modèles principaux

- **User** : Utilisateurs avec rôles
- **Etablissement** : Établissements scolaires
- **ComptePaiement** : Comptes Mobile Money
- **Etudiant** : Étudiants/élèves
- **Frais** : Frais scolaires
- **Paiement** : Transactions de paiement
- **Abonnement** : Abonnements des établissements
- **Facture** : Factures d'abonnement

## 🔒 Sécurité

- ✅ Authentification JWT
- ✅ Protection CSRF
- ✅ Validation des données serveur
- ✅ Permissions basées sur les rôles
- ✅ Logs immuables des transactions
- ✅ Variables secrètes via .env
- ✅ HTTPS obligatoire en production

## 📝 Logs

Les logs sont enregistrés dans `logs/edupay.log` et la console.

## 🤝 Contributeurs

Contributions bienvenues ! Merci de créer une issue avant de soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT.

## 🆘 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement

## 🚧 Fonctionnalités à venir

- [ ] Application mobile (Flutter)
- [ ] Notifications SMS
- [ ] Export Excel avancé
- [ ] Tableau de bord pour établissements
- [ ] Intégration avec systèmes de gestion scolaire
- [ ] Multi-devises automatique
- [ ] Rapports analytiques avancés

---

**Développé avec ❤️ pour l'éducation en RDC**


