"""
Vérification de la configuration SMS sans Django
"""
import os

def verifier_config_sms():
    """Vérifier la configuration SMS basique"""
    print("=" * 60)
    print("VÉRIFICATION CONFIGURATION SMS - EduPay RDC")
    print("=" * 60)
    print()
    
    # Vérifier le fichier render.yaml
    print("1. Configuration dans render.yaml:")
    print("-" * 60)
    
    try:
        with open('render.yaml', 'r') as f:
            content = f.read()
            
        if 'CINETPAY_SMS_API_KEY' in content:
            print("✅ CINETPAY_SMS_API_KEY trouvé dans render.yaml")
            # Extraire la valeur
            lines = content.split('\n')
            for line in lines:
                if 'CINETPAY_SMS_API_KEY' in line and 'value:' in line:
                    value = line.split('value:')[1].strip().strip('"')
                    print(f"   Valeur: {value[:10]}...{value[-4:] if len(value) > 14 else value}")
                    break
        else:
            print("❌ CINETPAY_SMS_API_KEY non trouvé dans render.yaml")
        
        if 'CINETPAY_SMS_SENDER_ID' in content:
            print("✅ CINETPAY_SMS_SENDER_ID trouvé dans render.yaml")
        else:
            print("❌ CINETPAY_SMS_SENDER_ID non trouvé dans render.yaml")
            
    except FileNotFoundError:
        print("❌ Fichier render.yaml non trouvé")
    print()
    
    # Vérifier les variables d'environnement actuelles
    print("2. Variables d'environnement actuelles:")
    print("-" * 60)
    
    sms_api_key = os.environ.get('CINETPAY_SMS_API_KEY', '')
    sms_sender_id = os.environ.get('CINETPAY_SMS_SENDER_ID', '')
    
    if sms_api_key:
        print(f"✅ CINETPAY_SMS_API_KEY: {sms_api_key[:10]}...{sms_api_key[-4:] if len(sms_api_key) > 14 else sms_api_key}")
    else:
        print("❌ CINETPAY_SMS_API_KEY: Non défini")
    
    if sms_sender_id:
        print(f"✅ CINETPAY_SMS_SENDER_ID: {sms_sender_id}")
    else:
        print("❌ CINETPAY_SMS_SENDER_ID: Non défini")
    print()
    
    # Analyse du problème
    print("3. Analyse du problème:")
    print("-" * 60)
    
    print("PROBLÈMES POSSIBLES:")
    print("1. Clé API SMS incorrecte ou inactive")
    print("2. Solde SMS insuffisant sur votre compte CinetPay")
    print("3. Numéro de téléphone incorrect dans le paiement")
    print("4. Format du numéro de téléphone (doit être au format international)")
    print("5. Service SMS CinetPay temporairement indisponible")
    print()
    
    print("VÉRIFICATIONS À FAIRE:")
    print("1. Connectez-vous à votre compte CinetPay")
    print("2. Vérifiez votre solde SMS")
    print("3. Vérifiez que la clé API est active")
    print("4. Testez l'envoi SMS depuis le dashboard CinetPay")
    print()
    
    print("INSTRUCTIONS POUR RÉSOUDRE:")
    print("-" * 60)
    print("Si vous n'avez PAS de clé API SMS:")
    print("1. Contactez support@cinetpay.com")
    print("2. Demandez l'activation du service SMS")
    print("3. Obtenez une clé API SMS dédiée")
    print("4. Ajoutez-la dans render.yaml")
    print()
    print("Si vous AVEZ une clé API SMS:")
    print("1. Vérifiez qu'elle est la même que dans render.yaml")
    print("2. Vérifiez votre solde SMS sur CinetPay")
    print("3. Testez avec un numéro de téléphone simple")
    print()
    
    print("FORMAT NUMÉRO TÉLÉPHONE:")
    print("-" * 60)
    print("✅ Format correct: +243900000000")
    print("✅ Format correct: 243900000000")
    print("❌ Format incorrect: 0900000000")
    print("❌ Format incorrect: +243 90 000 00 00")
    print()
    
    # Test API direct
    print("4. Test API direct (si clé disponible):")
    print("-" * 60)
    
    if sms_api_key:
        print("Clé API trouvée. Test de connexion...")
        try:
            import requests
            import json
            
            # Test simple de vérification de la clé
            headers = {
                'Authorization': f'App {sms_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Tenter une requête simple pour vérifier la clé
            test_payload = {
                'from': 'EDUPAY',
                'to': ['243123456789'],  # Numéro test
                'text': 'Test de configuration SMS EduPay'
            }
            
            response = requests.post(
                'https://api-notitia.cinetpay.com/sms/1/text/single',
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Connexion API réussie")
                print(f"Réponse: {json.dumps(result, indent=2)}")
            elif response.status_code == 401:
                print("❌ Erreur 401: Clé API invalide")
            elif response.status_code == 403:
                print("❌ Erreur 403: Accès refusé (solde insuffisant?)")
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
        except ImportError:
            print("⚠️  Module requests non disponible pour tester l'API")
    else:
        print("❌ Pas de clé API disponible pour tester")
    
    print()
    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print()
    print("Pour recevoir les SMS de confirmation:")
    print("1. Assurez-vous d'avoir une clé API SMS active")
    print("2. Vérifiez votre solde SMS sur CinetPay")
    print("3. Assurez-vous que le numéro de téléphone est correct")
    print("4. Le paiement doit avoir le statut 'SUCCESS'")
    print()

if __name__ == '__main__':
    verifier_config_sms()
