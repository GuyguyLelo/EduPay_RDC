# Guide de Déploiement - EduPay RDC

## 🚀 Préparation pour la Mise en Ligne

### 1. Configuration de la Base de Données PostgreSQL

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE edupay_rdc;

# Créer l'utilisateur (si nécessaire)
CREATE USER edupay_user WITH PASSWORD 'mohkandolo';

# Donner les privilèges
GRANT ALL PRIVILEGES ON DATABASE edupay_rdc TO edupay_user;

# Quitter
\q
```

### 2. Configuration des Variables d'Environnement

Le fichier `.env` est déjà configuré pour la production :

```bash
SECRET_KEY=NjeR0IB9zuhjZDwM37GAx5UjrjNeADHhjqkBLrheWNo3nDW1Sn_wQ7ZunPgWp7Do8BQ
DEBUG=False
DB_NAME=edupay_rdc
DB_USER=postgres
DB_PASSWORD=mohkandolo
DB_HOST=localhost
DB_PORT=5432
SITE_URL=https://votre-domaine.com
CINETPAY_API_KEY=2069229800671a567b9e80f4.35280533
CINETPAY_SITE_ID=5881999
CINETPAY_ENV=prod
```

### 3. Vérifications Avant Déploiement

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier la configuration Django
python manage.py check --deploy

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Créer un superutilisateur si nécessaire
python manage.py createsuperuser
```

### 4. Configuration du Serveur Web

#### Avec Gunicorn (Recommandé)

```bash
# Installer Gunicorn
pip install gunicorn

# Créer un fichier de service systemd
sudo nano /etc/systemd/system/edupay.service
```

Contenu du service :
```ini
[Unit]
Description=EduPay RDC Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/EduPay_RDC
EnvironmentFile=/chemin/vers/EduPay_RDC/.env
ExecStart=/chemin/vers/EduPay_RDC/venv/bin/gunicorn EduPay_RDC.wsgi:application --workers 3 --bind unix:/run/edupay.sock

[Install]
WantedBy=multi-user.target
```

```bash
# Démarrer et activer le service
sudo systemctl start edupay
sudo systemctl enable edupay
```

#### Avec Nginx

```bash
# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/edupay
```

Configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    
    # Redirection vers HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;
    
    # Certificat SSL (à obtenir avec Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    
    # Fichiers statiques
    location /static/ {
        alias /chemin/vers/EduPay_RDC/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Fichiers médias
    location /media/ {
        alias /chemin/vers/EduPay_RDC/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Application Django
    location / {
        proxy_pass http://unix:/run/edupay.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout pour les longues requêtes
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/edupay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Sécurité SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Configuration automatique du renouvellement
sudo crontab -e
# Ajouter cette ligne :
0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Configuration du Firewall

```bash
# Autoriser les ports nécessaires
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

### 7. Monitoring et Logs

```bash
# Logs de l'application
sudo journalctl -u edupay -f

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## 🔧 Vérifications Post-Déploiement

### Tests Automatiques

```bash
# Vérifier que l'application répond
curl -I https://votre-domaine.com

# Vérifier l'API
curl https://votre-domaine.com/api/auth/login/

# Vérifier les fichiers statiques
curl -I https://votre-domaine.com/static/admin/css/base.css
```

### Tests Fonctionnels

1. **Page d'accès** : Vérifier que la page se charge
2. **Connexion admin** : Tester l'accès au panneau d'administration
3. **Inscription étudiant** : Vérifier le processus d'inscription
4. **Paiement test** : Faire un petit paiement test
5. **Webhook CinetPay** : Vérifier la réception des notifications

## 🚨 Dépannage Commun

### Problèmes fréquents

1. **Erreur 502 Bad Gateway**
   - Vérifier que Gunicorn fonctionne : `sudo systemctl status edupay`
   - Vérifier les logs : `sudo journalctl -u edupay`

2. **Fichiers statiques non chargés**
   - Exécuter : `python manage.py collectstatic --noinput`
   - Vérifier les permissions Nginx

3. **Erreur de connexion à la base de données**
   - Vérifier que PostgreSQL fonctionne : `sudo systemctl status postgresql`
   - Vérifier les identifiants dans `.env`

4. **Erreur SSL**
   - Vérifier la configuration Certbot : `sudo certbot certificates`
   - Renouveler manuellement : `sudo certbot renew`

### Sauvegarde Automatique

```bash
# Script de sauvegarde
sudo nano /usr/local/bin/backup-edupay.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/edupay"
DB_NAME="edupay_rdc"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarder les fichiers médias
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /chemin/vers/EduPay_RDC/media/

# Supprimer les anciennes sauvegardes (+7 jours)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Rendre exécutable et planifier
sudo chmod +x /usr/local/bin/backup-edupay.sh
sudo crontab -e
# Ajouter : 0 2 * * * /usr/local/bin/backup-edupay.sh
```

## 📞 Support Déploiement

Pour toute assistance technique lors du déploiement :
- 📧 Email : tech@edupay-rdc.com
- 📞 Téléphone : +243 XXX XXX XXX
- 💬 WhatsApp : +243 XXX XXX XXX
