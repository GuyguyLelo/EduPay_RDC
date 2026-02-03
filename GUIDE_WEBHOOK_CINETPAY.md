# Guide de Configuration du Webhook CinetPay

## Introduction

Les webhooks permettent à CinetPay de notifier automatiquement votre application lorsqu'un paiement est effectué, échoué ou en attente. Cette configuration est essentielle pour mettre à jour automatiquement le statut des paiements dans votre système.

## URL du Webhook

L'URL du webhook pour EduPay RDC est :
```
https://votre-domaine.com/api/paiements/webhook/cinetpay/
```

## Configuration selon l'Environnement

### 1. Développement Local (localhost)

En développement local, `localhost` n'est pas accessible depuis Internet. Vous devez utiliser un tunnel pour exposer votre serveur local.

#### Option A : Utiliser ngrok (Recommandé)

1. **Installer ngrok** :
   ```bash
   # Télécharger depuis https://ngrok.com/download
   # Ou via npm: npm install -g ngrok
   ```

2. **Démarrer votre serveur Django** :
   ```bash
   python manage.py runserver
   ```

3. **Créer un tunnel ngrok** :
   ```bash
   ngrok http 8000
   ```

4. **Copier l'URL HTTPS fournie** (ex: `https://abc123.ngrok.io`)

5. **Mettre à jour `.env`** :
   ```env
   SITE_URL=https://abc123.ngrok.io
   ```

6. **Configurer le webhook dans CinetPay** :
   - URL : `https://abc123.ngrok.io/api/paiements/webhook/cinetpay/`
   - Note : L'URL ngrok change à chaque redémarrage (gratuit) ou utilisez un compte payant pour une URL fixe

#### Option B : Utiliser localtunnel

1. **Installer localtunnel** :
   ```bash
   npm install -g localtunnel
   ```

2. **Créer un tunnel** :
   ```bash
   lt --port 8000
   ```

3. **Utiliser l'URL fournie** dans la configuration CinetPay

### 2. Production

En production, utilisez votre domaine réel :

1. **Mettre à jour `.env`** :
   ```env
   SITE_URL=https://votre-domaine.com
   ```

2. **Configurer le webhook dans CinetPay** :
   - URL : `https://votre-domaine.com/api/paiements/webhook/cinetpay/`
   - Méthode : POST
   - Format : JSON

## Configuration dans l'Interface CinetPay

### Étapes de Configuration

1. **Connectez-vous** à votre interface marchand CinetPay
2. **Accédez** à la section **"Paramètres"** ou **"Intégration"**
3. **Trouvez** la section **"Webhooks"** ou **"Notifications"**
4. **Ajoutez** l'URL du webhook :
   ```
   https://votre-domaine.com/api/paiements/webhook/cinetpay/
   ```
5. **Activez** les événements suivants :
   - ✅ Paiement accepté (ACCEPTED)
   - ✅ Paiement refusé (REFUSED)
   - ✅ Paiement en attente (PENDING)
6. **Sauvegardez** la configuration

## Test du Webhook

### Test Manuel avec curl

```bash
curl -X POST https://votre-domaine.com/api/paiements/webhook/cinetpay/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpm_trans_id": "EDUPAY_123_1234567890",
    "status": "ACCEPTED",
    "amount": "10000",
    "currency": "CDF",
    "customer_name": "Test User",
    "customer_email": "test@example.com"
  }'
```

### Test avec CinetPay (Mode Test)

1. Effectuez un paiement de test dans votre application
2. Vérifiez les logs Django pour voir si le webhook est reçu
3. Vérifiez que le statut du paiement est mis à jour automatiquement

## Vérification des Logs

### Logs Django

Les webhooks sont loggés dans la console Django. Surveillez les messages :
- `"Webhook CinetPay reçu"`
- `"Paiement {id} confirmé via webhook CinetPay"`
- `"Erreur lors du traitement du webhook CinetPay"`

### Logs CinetPay

Dans votre interface CinetPay, vous pouvez voir :
- L'historique des tentatives de webhook
- Les statuts de livraison (succès/échec)
- Les codes de réponse HTTP

## Dépannage

### Problème : Webhook non reçu

**Solutions** :
1. Vérifiez que l'URL est accessible publiquement (pas de localhost)
2. Vérifiez que votre serveur Django est en cours d'exécution
3. Vérifiez les logs CinetPay pour voir les tentatives
4. Vérifiez que `ALLOWED_HOSTS` dans `settings.py` inclut votre domaine
5. Vérifiez les pare-feu et les règles de sécurité

### Problème : Erreur 404

**Solutions** :
1. Vérifiez que l'URL est correcte : `/api/paiements/webhook/cinetpay/`
2. Vérifiez que le serveur Django est accessible
3. Vérifiez que les routes sont correctement configurées

### Problème : Erreur 500

**Solutions** :
1. Vérifiez les logs Django pour l'erreur exacte
2. Vérifiez que la base de données est accessible
3. Vérifiez que les modèles sont correctement migrés
4. Vérifiez que les clés CinetPay sont correctement configurées

### Problème : Signature invalide

**Solutions** :
1. En mode test, la validation de signature est désactivée
2. En production, vérifiez que la validation de signature est implémentée
3. Vérifiez que l'API Key est correcte

## Sécurité

### Validation de la Signature (Production)

En production, il est recommandé de valider la signature du webhook. Le service `CinetPayService` inclut une méthode `valider_webhook()` qui peut être améliorée selon la documentation CinetPay.

### HTTPS Obligatoire

En production, utilisez **uniquement HTTPS** pour les webhooks. Les webhooks HTTP ne sont pas sécurisés.

### Rate Limiting

Considérez l'ajout d'un rate limiting pour protéger votre endpoint webhook contre les abus.

## Exemple de Configuration Complète

### Fichier `.env` (Production)

```env
# Site URL
SITE_URL=https://edupay-rdc.com

# CinetPay
CINETPAY_API_KEY=votre_api_key_production
CINETPAY_SITE_ID=votre_site_id_production
CINETPAY_ENV=prod
PAYMENT_GATEWAY=CINETPAY

# Django
DEBUG=False
ALLOWED_HOSTS=edupay-rdc.com,www.edupay-rdc.com
```

### URL Webhook dans CinetPay

```
https://edupay-rdc.com/api/paiements/webhook/cinetpay/
```

## Support

Pour toute question ou problème :
- **Documentation CinetPay** : [https://docs.cinetpay.com](https://docs.cinetpay.com)
- **Support CinetPay** : support@cinetpay.com
- **Logs Django** : Vérifiez la console ou les fichiers de logs





