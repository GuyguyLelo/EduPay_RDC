# 🚨 GUIDE CORRECTION SMS - EduPay RDC

## ❌ PROBLÈME IDENTIFIÉ

Vous ne recevez pas les SMS de confirmation car :

1. **Même clé API** pour paiements et SMS (INCORRECT)
2. **Clé API SMS** probablement non activée
3. **Solde SMS** peut-être insuffisant

## 🔍 DIAGNOSTIC COMPLET

### Configuration actuelle dans `render.yaml` :
```yaml
# ❌ INCORRECT - Même clé pour tout
CINETPAY_API_KEY: "200492077654f2b6c8e9e4.263965826"
CINETPAY_SMS_API_KEY: "200492077654f2b6c8e9e4.263965826"  # MÊME clé !
```

### Configuration correcte :
```yaml
# ✅ CORRECT - Clés séparées
CINETPAY_API_KEY: "200492077654f2b6c8e9e4.263965826"     # Pour les paiements
CINETPAY_SMS_API_KEY: "VOTRE_CLÉ_API_SMS_DÉDIÉE"        # Pour les SMS
```

## 🚀 SOLUTION ÉTAPE PAR ÉTAPE

### Étape 1 : Obtenir une clé API SMS dédiée

1. **Contactez CinetPay** :
   - 📧 Email : support@cinetpay.com
   - 📞 Téléphone : +225 2720 000 105 (Côte d'Ivoire)
   - 💬 WhatsApp : +225 07 777 777 77

2. **Demandez explicitement** :
   ```
   "Bonjour, je souhaite activer le service SMS pour mon application EduPay RDC.
   J'ai besoin d'une clé API SMS dédiée, différente de ma clé API paiements.
   Mon site ID : 578321"
   ```

3. **Informations à fournir** :
   - Votre nom/entreprise
   - Site ID : 578321
   - Usage : Notifications de paiement EduPay RDC
   - Pays : RDC (Congo-Kinshasa)

### Étape 2 : Configurer la clé SMS

1. **Une fois la clé SMS reçue**, modifiez `render.yaml` :
   ```yaml
   - key: CINETPAY_SMS_API_KEY
     value: "NOUVELLE_CLÉ_API_SMS_REÇUE"
   ```

2. **Vérifiez le Sender ID** :
   ```yaml
   - key: CINETPAY_SMS_SENDER_ID
     value: "EDUPAY"  # Doit être approuvé par CinetPay
   ```

### Étape 3 : Vérifier le solde SMS

1. **Connectez-vous** à votre dashboard CinetPay
2. **Vérifiez** :
   - Solde SMS disponible
   - Service SMS activé
   - Sender ID "EDUPAY" approuvé

### Étape 4 : Tester

1. **Déployez** les changements :
   ```bash
   git add render.yaml
   git commit -m "Config SMS dédiée"
   git push origin main
   ```

2. **Attendez 2-3 minutes** pour le déploiement

3. **Faites un test de paiement** pour vérifier les SMS

## 📋 FORMAT NUMÉRO TÉLÉPHONE

Assurez-vous que le numéro de téléphone est correct :

### ✅ Formats corrects :
- `+243900000000`
- `243900000000`

### ❌ Formats incorrects :
- `0900000000`
- `+243 90 000 00 00`
- `+243-90-000-00-00`

## 🔧 VÉRIFICATIONS TECHNIQUES

### 1. Logs Django
Après un paiement, vérifiez les logs pour :
```
SMS envoyé avec succès à +243XXXXXXX
```
ou
```
Erreur CinetPay SMS: API key invalid
```

### 2. Test manuel
Utilisez le script `verifier_config_sms.py` :
```bash
python3 verifier_config_sms.py
```

### 3. Dashboard CinetPay
Vérifiez dans votre dashboard :
- Historique des SMS envoyés
- Solde restant
- Statut du service

## 🆘 SI LE PROBLÈME PERSISTE

### Option 1 : Service SMS alternatif
Si CinetPay SMS ne fonctionne pas, nous pouvons intégrer :
- Orange SMS API
- AfricasTalking
- Twilio

### Option 2 : Email de confirmation
Activer les emails de confirmation en plus des SMS.

### Option 3 : Notification in-app
Ajouter des notifications dans le dashboard.

## 📞 CONTACTS CINETPAY

- **Support technique** : support@cinetpay.com
- **Service commercial** : commercial@cinetpay.com
- **WhatsApp** : +225 07 777 777 77
- **Site web** : https://cinetpay.com

## ⚡ RÉSUMÉ RAPIDE

1. **Contactez CinetPay** pour une clé API SMS dédiée
2. **Modifiez render.yaml** avec la nouvelle clé
3. **Vérifiez votre solde SMS**
4. **Testez avec un paiement réel**

## 🎯 OBJECTIF

Une fois configuré correctement, vous recevrez des SMS comme :
```
EDUPAY RDC - Paiement confirme
Montant: 50 USD
Frais: Frais d'inscription
Ref: CP123456789
Date: 09/02/2026 15:30
Merci pour votre confiance!
```

---

**Note importante** : Le service SMS est un service payant chez CinetPay. Assurez-vous d'avoir un solde suffisant pour envoyer les SMS de confirmation.
