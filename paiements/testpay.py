from cinetpay_sdk.s_d_k import Cinetpay
import time

apikey = "2069229800671a567b9e80f4.35280533"
site_id = "5881999"

print("Initialisation du client CinetPay...")
client = Cinetpay(apikey, site_id)
print(f"✅ Client CinetPay initialisé avec succès!")
print(f"   API Key: {apikey[:10]}...")
print(f"   Site ID: {site_id}")
print()

# ============================================
# TEST 1: Initialisation de paiement
# ============================================
print("=" * 60)
print("TEST 1: Initialisation de paiement")
print("=" * 60)

data = { 
    'amount': 1000,  # Montant (10.00 CDF)
    'currency': "CDF",  # Votre compte accepte CDF et USD, pas XOF
    'transaction_id': "TEST_" + str(int(time.time())),  # ID unique
    'description': "Test de paiement EduPay RDC",  
    'return_url': "https://www.exemple.com/return",
    'notify_url': "https://www.exemple.com/notify", 
    'customer_name': "Test",                              
    'customer_surname': "User",       
}  

try:
    print(f"Tentative d'initialisation de paiement...")
    print(f"Montant: {data['amount']} {data['currency']}")
    print(f"Transaction ID: {data['transaction_id']}")
    result = client.PaymentInitialization(data)
    print("✅ Résultat:")
    print(result)
    
    # Sauvegarder le token et transaction_id pour les tests suivants
    if result.get('code') == '201' and result.get('data'):
        payment_token = result['data'].get('payment_token')
        payment_url = result['data'].get('payment_url')
        saved_transaction_id = data['transaction_id']
        print(f"\n💡 Token obtenu: {payment_token[:50]}...")
        print(f"💡 URL de paiement: {payment_url}")
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    print(f"Type d'erreur: {type(e).__name__}")
    payment_token = None
    saved_transaction_id = None

print()
print()

# ============================================
# TEST 2: Vérification de transaction par transaction_id
# ============================================
print("=" * 60)
print("TEST 2: Vérification de transaction par transaction_id")
print("=" * 60)

# Utiliser le transaction_id du TEST 1 si disponible
transaction_id = saved_transaction_id if 'saved_transaction_id' in locals() else "TEST_XXXXXXXXXX"

try:
    print(f"Vérification de la transaction: {transaction_id}")
    result = client.TransactionVerfication_trx(transaction_id)
    print("✅ Résultat:")
    print(result)
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    print(f"Type d'erreur: {type(e).__name__}")
    print("ℹ️  Note: Utilisez un transaction_id réel pour tester")

print()
print()

# ============================================
# TEST 3: Vérification de transaction par token
# ============================================
print("=" * 60)
print("TEST 3: Vérification de transaction par token")
print("=" * 60)

# Utiliser le token du TEST 1 si disponible
token = payment_token if 'payment_token' in locals() and payment_token else "XXXXXX"

try:
    print(f"Vérification avec le token: {token}")
    result = client.TransactionVerfication_token(token)
    print("✅ Résultat:")
    print(result)
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    print(f"Type d'erreur: {type(e).__name__}")
    print("ℹ️  Note: Utilisez un token réel pour tester")
