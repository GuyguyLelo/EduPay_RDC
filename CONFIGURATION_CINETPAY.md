# Configuration CinetPay pour EduPay RDC

## Introduction

CinetPay est une passerelle de paiement spécialement conçue pour l'Afrique, offrant une excellente couverture des opérateurs Mobile Money en RDC (Orange Money, M-Pesa, Airtel Money, MTN, Moov).

## Étapes de Configuration

### 1. Création du Compte CinetPay

1. Visitez [https://www.cinetpay.com](https://www.cinetpay.com)
2. Créez un compte marchand
3. Complétez votre profil et vérifiez votre identité
4. Attendez la validation de votre compte (généralement 24-48h)

### 2. Création d'un Service Marchand

1. Connectez-vous à votre interface marchand CinetPay
2. Accédez à la section **"Services Marchands"**
3. Cliquez sur **"Créer un Service"**
4. Remplissez les informations requises :
   - Nom du service : "EduPay RDC"
   - Description : "Plateforme de paiement des frais scolaires"
   - Site web : Votre URL de production
5. Souscrivez à un abonnement annuel (nécessaire pour activer le service)
6. Une fois le service créé, notez :
   - **API Key** (clé API)
   - **Site ID** (identifiant du site)

### 3. Configuration dans EduPay RDC

#### 3.1. Installation des Dépendances

Les dépendances nécessaires sont déjà incluses dans `requirements.txt`. Installez-les avec :

```bash
pip install -r requirements.txt
```

**Note importante** : Le SDK CinetPay officiel est installé depuis PyPI test. Si l'installation échoue, utilisez :

```bash
pip install -i https://test.pypi.org/simple/ cinetpay-sdk==0.1.1
```

Consultez la [documentation officielle du SDK Python](https://docs.cinetpay.com/api/1.0-fr/sdk/python) pour plus d'informations.

#### 3.2. Configuration des Variables d'Environnement

Éditez votre fichier `.env` et ajoutez les informations CinetPay :

```env
# CinetPay Configuration
CINETPAY_API_KEY=votre_api_key_ici
CINETPAY_SITE_ID=votre_site_id_ici
CINETPAY_ENV=test  # test pour le développement, prod pour la production

# Choix de la passerelle de paiement
PAYMENT_GATEWAY=CINETPAY
```

**Important :**
- En mode **test**, utilisez les clés de test fournies par CinetPay
- En mode **prod**, utilisez les clés de production après validation de votre compte
- Ne partagez jamais vos clés API publiquement

#### 3.3. Configuration de l'URL de Webhook

Dans votre interface CinetPay :

1. Accédez à **"Paramètres"** > **"Webhooks"**
2. Configurez l'URL de notification :
   ```
   https://votre-domaine.com/api/paiements/webhook/cinetpay/
   ```
3. Activez les notifications pour les événements suivants :
   - Paiement accepté
   - Paiement refusé
   - Paiement en attente

### 4. Opérateurs Mobile Money Supportés

CinetPay supporte les opérateurs suivants en RDC :

- **Orange Money** (ORANGE)
- **M-Pesa** (MPESA)
- **Airtel Money** (AIRTEL)
- **MTN Mobile Money** (MTN)
- **Moov Money** (MOOV)

### 5. Méthodes de Paiement Disponibles

EduPay RDC utilise CinetPay pour trois méthodes de paiement :

#### 5.1. Mobile Money
- Paiement via téléphone mobile
- Confirmation par SMS/USSD
- Support de tous les opérateurs RDC

#### 5.2. Carte Bancaire
- Paiement par carte Visa/Mastercard
- Interface sécurisée CinetPay
- Redirection automatique après paiement

#### 5.3. QR Code
- Génération d'un QR Code unique
- Scan et paiement via application mobile
- Support de toutes les méthodes de paiement

### 6. Test de l'Intégration

#### 6.1. Mode Test

En mode test, utilisez les numéros de test fournis par CinetPay :

- **Orange Money** : `+243900000000`
- **M-Pesa** : `+243900000001`
- **Airtel Money** : `+243900000002`

#### 6.2. Scénarios de Test

1. **Test Mobile Money** :
   - Créez un paiement
   - Sélectionnez "Mobile Money"
   - Utilisez un numéro de test
   - Vérifiez la réception de la notification

2. **Test Carte Bancaire** :
   - Créez un paiement
   - Sélectionnez "Carte Bancaire"
   - Utilisez une carte de test (voir documentation CinetPay)
   - Vérifiez la redirection et le webhook

3. **Test QR Code** :
   - Créez un paiement
   - Sélectionnez "QR Code"
   - Scannez le QR Code généré
   - Vérifiez le paiement

### 7. Passage en Production

Avant de passer en production :

1. ✅ Vérifiez que tous les tests fonctionnent en mode test
2. ✅ Configurez les clés de production dans `.env`
3. ✅ Changez `CINETPAY_ENV=prod`
4. ✅ Configurez l'URL de webhook en production
5. ✅ Testez avec de vrais paiements de faible montant
6. ✅ Vérifiez les logs et les notifications

### 8. Monitoring et Logs

Les logs de paiement sont enregistrés dans :
- Console Django (mode développement)
- Fichiers de logs (mode production)
- Interface CinetPay (historique des transactions)

### 9. Support et Documentation

- **Documentation CinetPay** : [https://docs.cinetpay.com](https://docs.cinetpay.com)
- **Support CinetPay** : support@cinetpay.com
- **Documentation API** : [https://docs.cinetpay.com/api](https://docs.cinetpay.com/api)

### 10. Dépannage

#### Problème : "Clés CinetPay non configurées"
**Solution** : Vérifiez que `CINETPAY_API_KEY` et `CINETPAY_SITE_ID` sont bien définis dans `.env`

#### Problème : "Webhook non reçu"
**Solution** : 
- Vérifiez que l'URL de webhook est accessible publiquement
- Vérifiez les logs Django pour les erreurs
- Testez l'URL manuellement avec un outil comme Postman

#### Problème : "Paiement toujours en attente"
**Solution** :
- Vérifiez le statut dans l'interface CinetPay
- Utilisez la fonction de vérification manuelle
- Vérifiez les logs pour les erreurs de webhook

### 11. Comparaison CinetPay vs Flutterwave

| Fonctionnalité | CinetPay | Flutterwave |
|----------------|----------|-------------|
| Support Mobile Money RDC | ✅ Excellent | ⚠️ Limité |
| Frais de transaction | Variable | Variable |
| Support local | ✅ Oui (Afrique) | ⚠️ International |
| Documentation | ✅ Bonne | ✅ Excellente |
| Intégration Python | ✅ Facile | ✅ Facile |

**Recommandation** : CinetPay est recommandé pour la RDC en raison de son meilleur support des opérateurs locaux.

## Notes Importantes

- Les clés de test et de production sont différentes
- Les webhooks doivent être accessibles publiquement (pas de localhost en production)
- Les paiements en mode test ne sont pas réellement débités
- Conservez toujours une copie de vos clés API en sécurité
- Ne commitez jamais le fichier `.env` dans Git

