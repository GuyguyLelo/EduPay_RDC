# 🧪 Test Rapide - EduPay RDC

## Démarrage rapide

### 1. Démarrer le serveur

```bash
python manage.py runserver
```

Le serveur sera accessible sur : **http://localhost:8000**

---

## 🎯 Tests rapides (5 minutes)

### Test 1 : Connexion Étudiant

1. **Accéder à** : http://localhost:8000/
2. **Se connecter avec** :
   - Email: `etudiant1@test.com`
   - Mot de passe: `etudiant123`
3. **Vérifier** : Le tableau de bord étudiant s'affiche avec les frais à payer

---

### Test 2 : Paiement par QR Code ⭐ NOUVEAU

1. **Cliquer sur "Payer"** à côté d'un frais
2. **Sélectionner "📱 QR Code"** (option très rapide)
3. **Saisir l'email** : `etudiant1@test.com`
4. **Cliquer sur "Payer"**
5. **Vérifier** : 
   - ✅ QR Code affiché
   - ✅ Lien de paiement disponible
   - ✅ Vérification automatique active

**Temps estimé** : 30 secondes

---

### Test 3 : Paiement par Carte Bancaire

1. **Cliquer sur "Payer"** à côté d'un frais
2. **Sélectionner "💳 Carte Bancaire"** (option rapide)
3. **Saisir l'email** : `etudiant1@test.com`
4. **Cliquer sur "Payer"**
5. **Vérifier** : Redirection vers Flutterwave (si clés configurées)

**Temps estimé** : 20 secondes

---

### Test 4 : Paiement par Mobile Money

1. **Cliquer sur "Payer"** à côté d'un frais
2. **Sélectionner "📱 Mobile Money"**
3. **Remplir** :
   - Numéro: `+243900000010`
   - Opérateur: `M-Pesa`
4. **Cliquer sur "Payer"**
5. **Vérifier** : Message de succès et statut "En attente"

**Temps estimé** : 30 secondes

---

### Test 5 : Voir les détails d'un paiement

1. **Aller dans l'historique des paiements**
2. **Cliquer sur "Vérifier"** à côté d'un paiement en attente
3. **Vérifier** : Statut mis à jour

---

### Test 6 : Gestion Admin Établissement

1. **Se connecter avec** :
   - Email: `admin.etab@test.com`
   - Mot de passe: `admin123`

2. **Tester les fonctionnalités** :
   - ✅ Voir le dashboard
   - ✅ Voir la liste des étudiants
   - ✅ Voir les détails d'un étudiant
   - ✅ Modifier un étudiant
   - ✅ Voir la liste des frais
   - ✅ Voir les détails d'un frais
   - ✅ Modifier un frais
   - ✅ Voir la liste des comptes Mobile Money
   - ✅ Voir les détails d'un compte
   - ✅ Modifier un compte

---

## ✅ Checklist rapide

- [ ] Connexion étudiant fonctionne
- [ ] Tableau de bord étudiant s'affiche
- [ ] Page de paiement s'affiche
- [ ] Choix de méthode de paiement fonctionne
- [ ] QR Code s'affiche correctement
- [ ] Carte bancaire redirige vers Flutterwave
- [ ] Mobile Money initie le paiement
- [ ] Vérification du statut fonctionne
- [ ] Dashboard admin établissement fonctionne
- [ ] Toutes les pages de détails s'affichent
- [ ] Tous les formulaires de modification fonctionnent

---

## 🐛 Problèmes courants

### Le serveur ne démarre pas
```bash
# Vérifier les migrations
python manage.py migrate

# Vérifier la configuration
python manage.py check
```

### Erreur Flutterwave
- Créez un fichier `.env` avec les clés (voir `CONFIGURATION_FLUTTERWAVE.md`)
- Ou testez sans clés (les paiements seront créés mais non complétés)

### QR Code ne s'affiche pas
```bash
pip install qrcode[pil]
```

---

## 📊 Données de test disponibles

### Étudiants
- `etudiant1@test.com` / `etudiant123`
- `etudiant2@test.com` / `etudiant123`
- `etudiant3@test.com` / `etudiant123`

### Admin Établissement
- `admin.etab@test.com` / `admin123`

### Super Admin
- `admin@edupay-rdc.com` / `admin123`

### Frais disponibles
- Frais de scolarité : 50,000 CDF
- Frais d'inscription : 25,000 CDF
- Frais de bibliothèque : 10,000 CDF

---

**Temps total de test** : ~5-10 minutes

**Note** : Pour tester les paiements réels, configurez Flutterwave dans `.env`





