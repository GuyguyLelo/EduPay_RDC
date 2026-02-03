# Guide de Test - EduPay RDC

## 🧪 Tests des fonctionnalités de paiement

### Prérequis

1. ✅ Serveur Django en cours d'exécution
2. ✅ Base de données migrée
3. ✅ Données de test créées (voir `create_test_data.py`)
4. ⚠️ Clés Flutterwave configurées dans `.env` (optionnel pour les tests)

### Scénarios de test

## Test 1 : Connexion en tant qu'étudiant

1. **Accéder à la page de connexion**
   - URL: `http://localhost:8000/`
   - La page de login devrait s'afficher

2. **Se connecter avec un compte étudiant**
   - Email: `etudiant1@test.com`
   - Mot de passe: `etudiant123`
   - Cliquer sur "Se connecter"

3. **Vérifier le tableau de bord étudiant**
   - Vous devriez voir vos informations
   - Section "Mes Frais à Payer" avec les frais disponibles
   - Section "Historique des Paiements"

---

## Test 2 : Paiement par QR Code (Nouveau - Très Rapide)

1. **Accéder à la page de paiement**
   - Cliquer sur "Payer" à côté d'un frais
   - URL: `http://localhost:8000/paiement/payer/1/`

2. **Choisir la méthode QR Code**
   - Sélectionner la carte "📱 QR Code" (option très rapide)
   - Le formulaire QR Code devrait s'afficher

3. **Saisir l'email**
   - Email: `etudiant1@test.com` (pré-rempli)
   - Cliquer sur "Payer"

4. **Vérifier l'affichage du QR Code**
   - Une page avec le QR Code devrait s'afficher
   - Le QR Code devrait être visible et scannable
   - Un lien de paiement alternatif devrait être disponible

5. **Tester la vérification automatique**
   - La page vérifie automatiquement le statut toutes les 5 secondes
   - Cliquer sur "Vérifier le paiement" pour vérification manuelle

**Résultat attendu :**
- ✅ QR Code généré et affiché
- ✅ Lien de paiement disponible
- ✅ Vérification automatique fonctionnelle

---

## Test 3 : Paiement par Carte Bancaire (Rapide)

1. **Accéder à la page de paiement**
   - Cliquer sur "Payer" à côté d'un frais

2. **Choisir la méthode Carte Bancaire**
   - Sélectionner la carte "💳 Carte Bancaire" (option rapide)
   - Le formulaire carte devrait s'afficher

3. **Saisir l'email**
   - Email: `etudiant1@test.com`
   - Cliquer sur "Payer"

4. **Redirection vers Flutterwave**
   - Vous devriez être redirigé vers la page de paiement Flutterwave
   - (En mode sandbox, utilisez les cartes de test)

**Résultat attendu :**
- ✅ Redirection vers Flutterwave
- ✅ Page de paiement sécurisée affichée

---

## Test 4 : Paiement par Mobile Money (Standard)

1. **Accéder à la page de paiement**
   - Cliquer sur "Payer" à côté d'un frais

2. **Choisir la méthode Mobile Money**
   - Sélectionner la carte "📱 Mobile Money"
   - Le formulaire Mobile Money devrait s'afficher

3. **Remplir le formulaire**
   - Numéro de téléphone: `+243900000010`
   - Opérateur: `M-Pesa` (ou Orange Money, Airtel Money)
   - Cliquer sur "Payer"

4. **Vérifier l'initiation du paiement**
   - Message de succès devrait s'afficher
   - Redirection vers la page de succès
   - Statut "En attente" dans l'historique

**Résultat attendu :**
- ✅ Paiement initié avec succès
- ✅ Message de confirmation affiché
- ✅ Statut "En attente" dans l'historique

---

## Test 5 : Vérification du statut d'un paiement

1. **Accéder à l'historique des paiements**
   - Tableau de bord étudiant
   - Section "Historique des Paiements"

2. **Vérifier un paiement en attente**
   - Cliquer sur "Vérifier" à côté d'un paiement en attente
   - Le statut devrait être mis à jour

**Résultat attendu :**
- ✅ Statut mis à jour automatiquement
- ✅ Message de confirmation si le paiement est réussi

---

## Test 6 : Téléchargement du reçu PDF

1. **Accéder à un paiement réussi**
   - Dans l'historique, trouver un paiement avec statut "Réussi"
   - Cliquer sur "Reçu"

2. **Vérifier le téléchargement**
   - Un fichier PDF devrait être téléchargé
   - Le PDF devrait contenir les détails du paiement

**Résultat attendu :**
- ✅ PDF téléchargé avec succès
- ✅ Contenu du reçu correct

---

## Test 7 : Gestion des établissements (Super Admin)

1. **Se connecter en tant que Super Admin**
   - Email: `admin@edupay-rdc.com`
   - Mot de passe: `admin123`

2. **Accéder au dashboard admin**
   - URL: `http://localhost:8000/dashboard/`
   - Vérifier les statistiques

3. **Gérer les établissements**
   - Aller dans "Établissements"
   - Voir les détails d'un établissement
   - Modifier un établissement
   - Activer/Suspendre un établissement

**Résultat attendu :**
- ✅ Dashboard affiché avec statistiques
- ✅ Liste des établissements visible
- ✅ Actions (détails, modifier, activer/suspendre) fonctionnelles

---

## Test 8 : Gestion des étudiants (Admin Établissement)

1. **Se connecter en tant qu'admin d'établissement**
   - Email: `admin.etab@test.com`
   - Mot de passe: `admin123`

2. **Accéder au dashboard établissement**
   - URL: `http://localhost:8000/etablissement/dashboard/`
   - Vérifier les statistiques

3. **Gérer les étudiants**
   - Aller dans "Étudiants"
   - Ajouter un nouvel étudiant
   - Voir les détails d'un étudiant
   - Modifier un étudiant

**Résultat attendu :**
- ✅ Dashboard établissement affiché
- ✅ Liste des étudiants visible
- ✅ Formulaire d'ajout fonctionnel
- ✅ Actions (détails, modifier) fonctionnelles

---

## Test 9 : Gestion des frais (Admin Établissement)

1. **Se connecter en tant qu'admin d'établissement**

2. **Gérer les frais**
   - Aller dans "Frais"
   - Ajouter de nouveaux frais
   - Voir les détails d'un frais
   - Modifier un frais

**Résultat attendu :**
- ✅ Liste des frais visible
- ✅ Formulaire d'ajout fonctionnel
- ✅ Actions (détails, modifier) fonctionnelles

---

## Test 10 : Gestion des comptes Mobile Money (Admin Établissement)

1. **Se connecter en tant qu'admin d'établissement**

2. **Gérer les comptes Mobile Money**
   - Aller dans "Comptes Mobile Money"
   - Ajouter un nouveau compte
   - Voir les détails d'un compte
   - Modifier un compte

**Résultat attendu :**
- ✅ Liste des comptes visible
- ✅ Formulaire d'ajout fonctionnel avec champ "Intitulé"
- ✅ Actions (détails, modifier) fonctionnelles

---

## ⚠️ Tests nécessitant Flutterwave

Pour tester les paiements réels, vous devez :

1. **Créer un compte Flutterwave**
   - Aller sur https://dashboard.flutterwave.com/
   - Créer un compte (gratuit)

2. **Obtenir les clés Sandbox**
   - Aller dans Settings > API Keys
   - Copier la Public Key et Secret Key (mode Sandbox)

3. **Configurer le fichier .env**
   ```env
   FLUTTERWAVE_PUBLIC_KEY=FLWPUBK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   FLUTTERWAVE_SECRET_KEY=FLWSECK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   FLUTTERWAVE_ENV=sandbox
   ```

4. **Redémarrer le serveur**
   ```bash
   python manage.py runserver
   ```

5. **Tester avec les numéros de test Flutterwave**
   - Consultez la documentation Flutterwave pour les numéros de test
   - Utilisez les cartes de test pour les paiements par carte

---

## ✅ Checklist de test

### Fonctionnalités de base
- [ ] Connexion/Déconnexion
- [ ] Tableau de bord étudiant
- [ ] Tableau de bord établissement
- [ ] Tableau de bord super admin

### Gestion des entités
- [ ] Création d'établissement
- [ ] Modification d'établissement
- [ ] Détails d'établissement
- [ ] Création d'étudiant
- [ ] Modification d'étudiant
- [ ] Détails d'étudiant
- [ ] Création de frais
- [ ] Modification de frais
- [ ] Détails de frais
- [ ] Création de compte Mobile Money
- [ ] Modification de compte Mobile Money
- [ ] Détails de compte Mobile Money

### Paiements
- [ ] Paiement par QR Code
- [ ] Paiement par Carte Bancaire
- [ ] Paiement par Mobile Money
- [ ] Vérification du statut
- [ ] Téléchargement du reçu PDF

### Sécurité
- [ ] Accès refusé pour utilisateurs non autorisés
- [ ] Validation des formulaires
- [ ] Protection CSRF

---

## 🐛 Dépannage

### Erreur : "Clés Flutterwave non configurées"
**Solution :** Créez un fichier `.env` avec les clés Flutterwave (voir `CONFIGURATION_FLUTTERWAVE.md`)

### Erreur : "TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'"
**Solution :** Vérifiez que `COMMISSION_RATE` est bien un Decimal dans `settings.py`

### Erreur : "NoReverseMatch"
**Solution :** Vérifiez que toutes les URLs sont correctement configurées

### Le QR Code ne s'affiche pas
**Solution :** Vérifiez que `qrcode[pil]` est installé : `pip install qrcode[pil]`

---

## 📊 Résultats attendus

Après tous les tests, vous devriez avoir :
- ✅ 1 établissement créé
- ✅ 3 étudiants créés
- ✅ 3 frais créés
- ✅ 1 compte Mobile Money créé
- ✅ Plusieurs paiements testés (QR Code, Carte, Mobile Money)

---

**Note :** En mode développement sans clés Flutterwave, les paiements seront créés mais ne pourront pas être complétés. Configurez Flutterwave pour tester les paiements réels.





