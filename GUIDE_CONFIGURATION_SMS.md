# Guide de Configuration SMS pour les Confirmations de Paiement

## Introduction

Ce guide explique comment configurer l'envoi de SMS de confirmation de paiement via l'API SMS de CinetPay. Les confirmations sont maintenant envoyées par SMS au lieu d'email.

## Étapes de Configuration

### 1. Créer un Compte SMS chez CinetPay

L'API SMS est distincte du compte marchand. Pour obtenir un compte SMS :

1. Contactez CinetPay à l'adresse : **support@cinetpay.com**
2. Demandez la création d'un compte SMS
3. Attendez la validation de votre compte

### 2. Obtenir votre Clé API SMS

Une fois votre compte SMS créé :

1. Connectez-vous à votre espace client CinetPay
2. Accédez au menu **"Mon compte"**
3. Cliquez sur **"Gérer les clés API"**
4. Générez une clé API SMS
5. Notez cette clé (vous en aurez besoin pour la configuration)

### 3. Configuration dans EduPay RDC

#### 3.1. Variables d'Environnement

Éditez votre fichier `.env` et ajoutez :

```env
# CinetPay SMS (pour les confirmations par SMS)
CINETPAY_SMS_API_KEY=votre_cle_api_sms_ici
CINETPAY_SMS_SENDER_ID=EDUPAY
```

**Explication des variables :**
- `CINETPAY_SMS_API_KEY` : Votre clé API SMS obtenue depuis CinetPay
- `CINETPAY_SMS_SENDER_ID` : ID de l'expéditeur (3-11 caractères alphanumériques)
  - Par défaut : `EDUPAY`
  - Exemples valides : `EDUPAY`, `EDUPAY_RDC`, `ECOLE123`
  - ⚠️ L'ID doit être approuvé par CinetPay avant utilisation

#### 3.2. Format du Numéro de Téléphone

Les numéros de téléphone doivent être au format international **sans le signe +** pour l'API SMS :

✅ **Format correct** : `243900000000` (sans le +)  
❌ **Format incorrect** : `+243900000000` (avec le +)

Le service normalise automatiquement le numéro en enlevant le `+`.

### 4. Fonctionnement

#### 4.1. Quand un SMS est Envoyé

Un SMS de confirmation est automatiquement envoyé lorsque :
- Un paiement est confirmé comme réussi (statut SUCCESS)
- Le paiement passe par le webhook CinetPay
- Le paiement est vérifié manuellement et confirmé

#### 4.2. Contenu du SMS

Le SMS contient :
```
EDUPAY RDC - Paiement confirme
Montant: 10000 CDF
Frais: Frais de scolarité
Ref: REC-000001
Date: 15/01/2024 14:30
Merci pour votre confiance!
```

#### 4.3. Numéro de Téléphone Utilisé

Le système utilise dans l'ordre :
1. Le numéro de téléphone du paiement (`paiement.numero_telephone`)
2. Le numéro de téléphone de l'étudiant (`paiement.etudiant.telephone`)
3. Si aucun numéro n'est disponible, le SMS n'est pas envoyé (mais le paiement reste valide)

### 5. Test

#### 5.1. Vérifier la Configuration

1. Vérifiez que `CINETPAY_SMS_API_KEY` est configuré dans `.env`
2. Vérifiez que `CINETPAY_SMS_SENDER_ID` est configuré (par défaut `EDUPAY`)
3. Redémarrez le serveur Django si nécessaire

#### 5.2. Test d'Envoi

1. Effectuez un paiement de test
2. Attendez la confirmation du paiement
3. Vérifiez que le SMS est reçu sur le numéro utilisé
4. Vérifiez les logs Django pour voir les détails de l'envoi

### 6. Dépannage

#### Problème : SMS non reçu

**Solutions :**
1. ✅ Vérifiez que `CINETPAY_SMS_API_KEY` est correctement configuré
2. ✅ Vérifiez que le numéro de téléphone est au bon format
3. ✅ Vérifiez les logs Django pour les erreurs
4. ✅ Vérifiez que votre compte SMS CinetPay est actif
5. ✅ Vérifiez que l'ID expéditeur (`CINETPAY_SMS_SENDER_ID`) est approuvé par CinetPay

#### Problème : "Clé API SMS non configurée"

**Solution :**
- Ajoutez `CINETPAY_SMS_API_KEY` dans votre fichier `.env`
- Redémarrez le serveur Django

#### Problème : "Aucun numéro de téléphone disponible"

**Solution :**
- Assurez-vous que le numéro de téléphone est renseigné lors du paiement
- Ou que l'étudiant a un numéro de téléphone dans son profil

#### Problème : Erreur d'authentification API

**Solutions :**
1. Vérifiez que votre clé API SMS est correcte
2. Vérifiez que votre compte SMS est actif
3. Contactez le support CinetPay si le problème persiste

### 7. Logs

Les logs d'envoi de SMS sont enregistrés avec le logger Django. Surveillez les messages :

- `SMS envoyé avec succès à {numéro}`
- `Échec de l'envoi du SMS pour le paiement {id}`
- `Service SMS non disponible pour le paiement {id}`

### 8. Coûts

⚠️ **Important** : L'envoi de SMS via l'API CinetPay SMS est payant. Les tarifs dépendent de votre contrat avec CinetPay. Consultez votre facture CinetPay pour plus d'informations.

### 9. Alternative : Désactiver les SMS

Si vous préférez ne pas envoyer de SMS :

1. Ne configurez pas `CINETPAY_SMS_API_KEY` dans `.env`
2. Le système n'enverra pas de SMS (mais le paiement restera valide)
3. Les logs afficheront un avertissement mais n'empêcheront pas le paiement

### 10. Documentation CinetPay SMS

Pour plus d'informations sur l'API SMS de CinetPay :
- **Documentation** : https://docs.cinetpay.com/api/1.0-fr/sms/
- **Support** : support@cinetpay.com

## Notes Importantes

- ⚠️ L'envoi de SMS est **asynchrone** et peut prendre quelques secondes
- ⚠️ Si l'envoi du SMS échoue, **le paiement reste valide**
- ⚠️ Les SMS sont **payants**, vérifiez vos tarifs avec CinetPay
- ⚠️ L'ID expéditeur (`CINETPAY_SMS_SENDER_ID`) doit être approuvé par CinetPay avant utilisation
- ⚠️ Le format du numéro doit être sans le signe `+` (normalisé automatiquement)

## Support

Pour toute question ou problème :
- **Documentation CinetPay SMS** : https://docs.cinetpay.com/api/1.0-fr/sms/
- **Support CinetPay** : support@cinetpay.com
- **Logs Django** : Vérifiez la console ou les fichiers de logs





