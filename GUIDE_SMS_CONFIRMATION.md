# Guide : Recevoir le SMS de Confirmation CinetPay

## Problème : Je ne reçois pas le SMS de confirmation

Si vous ne recevez pas le SMS de confirmation lors d'un paiement Mobile Money via CinetPay, suivez ce guide de dépannage.

## Solutions

### 1. Vérifier le Format du Numéro de Téléphone

Le numéro de téléphone **doit** être au format international avec le préfixe `+243` pour la RDC :

✅ **Format correct** :
- `+243900000000` (Orange Money)
- `+243812345678` (M-Pesa)
- `+243991234567` (Airtel Money)

❌ **Format incorrect** :
- `0900000000` (manque le préfixe +243)
- `243900000000` (manque le signe +)
- `009900000000` (double zéro)

### 2. Utiliser les Numéros de Test (Mode Test)

Si vous êtes en mode **test** (`CINETPAY_ENV=test`), utilisez les numéros de test fournis par CinetPay :

- **Orange Money** : `+243900000000`
- **M-Pesa** : `+243900000001`
- **Airtel Money** : `+243900000002`
- **MTN** : `+243900000003`
- **Moov** : `+243900000004`

⚠️ **Important** : En mode test, vous ne recevrez pas de vrai SMS, mais le paiement sera simulé dans l'interface CinetPay.

### 3. Vérifier l'Opérateur

Le numéro de téléphone **doit correspondre** à l'opérateur Mobile Money sélectionné :

- Numéro Orange → Opérateur **Orange Money**
- Numéro Airtel → Opérateur **Airtel Money**
- Numéro M-Pesa → Opérateur **M-Pesa**

### 4. Vérifications Techniques

#### A. Réception des SMS

1. ✅ Vérifiez que votre téléphone peut recevoir des SMS
2. ✅ Vérifiez que vous avez du signal réseau
3. ✅ Vérifiez que votre téléphone n'est pas en mode avion
4. ✅ Vérifiez les filtres de messages (spam, bloqueur)

#### B. Configuration CinetPay

1. ✅ Vérifiez que votre compte CinetPay est activé
2. ✅ Vérifiez que votre service marchand est actif
3. ✅ Vérifiez que les notifications SMS sont activées dans votre interface CinetPay

### 5. Processus de Paiement Mobile Money

Avec CinetPay, le processus peut varier selon la configuration :

#### Option A : Redirection vers une page de paiement

1. Le système génère une URL de paiement
2. L'utilisateur est redirigé vers la page CinetPay
3. L'utilisateur entre son numéro de téléphone sur la page CinetPay
4. CinetPay envoie le SMS de confirmation
5. L'utilisateur confirme sur son téléphone

#### Option B : Paiement direct (si configuré)

1. Le numéro de téléphone est envoyé directement à CinetPay
2. CinetPay envoie le SMS de confirmation
3. L'utilisateur confirme sur son téléphone
4. Le paiement est validé

### 6. Comment le Code Gère le Numéro de Téléphone

Dans le code actuel, le numéro de téléphone est inclus dans les données envoyées à CinetPay :

```python
data = {
    'amount': amount,
    'currency': paiement.devise,
    'transaction_id': transaction_id,
    'customer_phone_number': numero_telephone,  # ← Numéro inclus
    'customer_email': paiement.etudiant.user.email,
    # ... autres paramètres
}
```

### 7. Vérifier les Logs

Si le SMS n'arrive toujours pas, vérifiez les logs Django :

```bash
# Dans les logs, recherchez :
- "Paiement CinetPay {id} initié avec succès"
- "Réponse CinetPay pour paiement {id}"
```

Si vous voyez une erreur, notez le message d'erreur.

### 8. Délai de Réception

- Les SMS peuvent prendre **1 à 5 minutes** à arriver
- Si après 5 minutes vous n'avez rien reçu, vérifiez votre numéro
- Certains opérateurs peuvent avoir des délais plus longs

### 9. Contacter le Support CinetPay

Si le problème persiste :

1. **Vérifiez votre compte CinetPay** :
   - Connectez-vous à votre interface marchand
   - Vérifiez l'historique des transactions
   - Regardez les détails de la transaction

2. **Contactez le support CinetPay** :
   - Email : support@cinetpay.com
   - Site web : https://cinetpay.com/contact
   - Fournissez votre `transaction_id` et le numéro de téléphone utilisé

### 10. Alternative : Utiliser Carte Bancaire ou QR Code

Si les SMS ne fonctionnent pas de manière fiable, vous pouvez utiliser :

- **Carte Bancaire** : Paiement direct sans SMS
- **QR Code** : Scan et paiement via application mobile

Ces méthodes sont souvent plus rapides et ne nécessitent pas de SMS de confirmation.

## Checklist de Dépannage

Avant de contacter le support, vérifiez :

- [ ] Le numéro est au format international (+243...)
- [ ] Le numéro correspond à l'opérateur sélectionné
- [ ] En mode test, vous utilisez un numéro de test
- [ ] Votre téléphone peut recevoir des SMS
- [ ] Vous avez du signal réseau
- [ ] Le compte CinetPay est actif
- [ ] Les logs ne montrent pas d'erreur
- [ ] Vous avez attendu au moins 5 minutes

## Exemples de Numéros Valides

### RDC - Format International

```
Orange Money :
+243900000000
+243812345678
+243991234567

Airtel Money :
+243991234567
+243812345678

M-Pesa :
+243812345678
```

### Format dans le Formulaire

Dans le formulaire de paiement, entrez le numéro au format :
```
+243900000000
```

**Ne pas utiliser** :
- Espaces : `+243 900 000 000` ❌
- Tirets : `+243-900-000-000` ❌
- Parenthèses : `+243(900)000000` ❌

## Conclusion

Le SMS de confirmation dépend de plusieurs facteurs. Si vous suivez ce guide et que le problème persiste, contactez le support CinetPay avec les détails de votre transaction.





