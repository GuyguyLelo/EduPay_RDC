"""
Vues templates pour les paiements
"""
import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from frais.models import Frais
from .models import Paiement, StatutPaiement
from .services_cinetpay import CinetPayService
from .receipts import generate_receipt_pdf

logger = logging.getLogger(__name__)


@login_required
def payer_frais(request, frais_id):
    """
    Page de paiement d'un frais - Méthode CinetPay Seamless (SDK JavaScript).
    Étape 1: formulaire coordonnées client.
    Étape 2: bouton qui ouvre CinetPay.getCheckout() (Mobile Money, Carte, etc.).
    """
    if not request.user.is_etudiant:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    frais = get_object_or_404(Frais, id=frais_id, actif=True)
    etudiant = request.user.etudiant
    
    if frais.etablissement != etudiant.etablissement:
        messages.error(request, "Ce frais ne vous concerne pas.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    paiement_existant = Paiement.objects.filter(
        etudiant=etudiant,
        frais=frais,
        statut=StatutPaiement.SUCCESS
    ).first()
    
    if paiement_existant:
        messages.info(request, "Ce frais a déjà été payé.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    if request.method == 'POST':
        # Vérifier la configuration CinetPay
        api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        if not api_key or not site_id:
            messages.error(request, "Paiement non configuré. Veuillez contacter l'administrateur.")
            return redirect('etudiants_templates:etudiant_dashboard')
        
        customer_name = request.POST.get('customer_name', '').strip() or etudiant.nom
        customer_surname = request.POST.get('customer_surname', '').strip() or etudiant.prenom
        customer_email = request.POST.get('customer_email', '').strip() or request.user.email
        customer_phone_number = request.POST.get('customer_phone_number', '').strip()
        
        if not customer_phone_number:
            messages.error(request, "Le numéro de téléphone est obligatoire.")
            return render(request, 'paiements/payer.html', {
                'frais': frais,
                'etudiant': etudiant,
                'has_operator_error': False
            })
        
        # Créer le paiement
        paiement = Paiement.objects.create(
            etudiant=etudiant,
            frais=frais,
            montant=frais.montant,
            devise=frais.devise,
            methode_paiement='MOBILE_MONEY',  # Seamless gère tous les canaux
            statut=StatutPaiement.PENDING,
            taux_commission=getattr(settings, 'COMMISSION_RATE', 2.0),
            numero_telephone=customer_phone_number,
            email_paiement=customer_email or None
        )
        
        # ID de transaction unique pour CinetPay (et pour le webhook)
        transaction_id = f"EDUPAY_{paiement.id}_{int(time.time())}"
        paiement.transaction_id = transaction_id
        paiement.reference_flutterwave = transaction_id
        paiement.save()
        
        # URL de notification pour le webhook
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
        try:
            notify_path = reverse('paiements:webhook_cinetpay')
            notify_url = f"{site_url}{notify_path}"
        except Exception:
            notify_url = f"{site_url}/api/paiements/webhook/cinetpay/"
        
        cinetpay_config = {
            'apikey': api_key,
            'site_id': site_id,
            'notify_url': notify_url,
            'mode': getattr(settings, 'CINETPAY_ENV', 'test')
        }
        
        # Montant: pour CDF pas de décimales, pour USD 2 décimales
        amount_float = float(paiement.montant)
        if paiement.devise == 'CDF':
            amount_float = int(amount_float)
        
        description = f"Paiement {frais.nom_frais} - {frais.etablissement.nom}"
        
        context = {
            'frais': frais,
            'etudiant': etudiant,
            'paiement': paiement,
            'cinetpay_config': cinetpay_config,
            'checkout_transaction_id': transaction_id,
            'checkout_amount': amount_float,
            'checkout_currency': paiement.devise,
            'checkout_description': description,
            'customer_name': customer_name,
            'customer_surname': customer_surname,
            'customer_email': customer_email,
            'customer_phone_number': customer_phone_number,
            'customer_address': request.POST.get('customer_address', '') or 'N/A',
            'customer_city': request.POST.get('customer_city', '') or 'Kinshasa',
            'customer_country': request.POST.get('customer_country', '') or 'CD',
            'customer_state': request.POST.get('customer_state', '') or 'CD',
            'customer_zip_code': request.POST.get('customer_zip_code', '') or '00000',
            'has_operator_error': False
        }
        return render(request, 'paiements/payer.html', context)
    
    # GET: afficher le formulaire coordonnées
    error_messages = list(messages.get_messages(request))
    has_operator_error = any('opérateur' in str(m).lower() or 'operator' in str(m).lower() for m in error_messages)
    
    return render(request, 'paiements/payer.html', {
        'frais': frais,
        'etudiant': etudiant,
        'has_operator_error': has_operator_error
    })


@login_required
def paiement_success(request, paiement_id):
    """Page de succès du paiement"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement appartient à l'utilisateur
    if request.user.is_etudiant and paiement.etudiant.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    return render(request, 'paiements/success.html', {'paiement': paiement})


@login_required
def paiement_qr_code(request, paiement_id):
    """Affiche le QR Code pour le paiement"""
    if not request.user.is_etudiant:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement appartient à l'étudiant
    if paiement.etudiant.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    # Vérifier que c'est un paiement QR Code
    if paiement.methode_paiement != 'QR_CODE':
        messages.error(request, "Ce paiement n'utilise pas la méthode QR Code.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    # Générer le QR Code
    import qrcode
    from io import BytesIO
    import base64
    from django.conf import settings
    
    # Récupérer le lien de paiement
    payment_link = None
    
    # Pour CinetPay, le payment_link est stocké dans message_erreur pour les QR Codes
    if paiement.message_erreur and paiement.message_erreur.startswith('http'):
        payment_link = paiement.message_erreur
    elif paiement.reference_flutterwave and paiement.reference_flutterwave.startswith('http'):
        payment_link = paiement.reference_flutterwave
    
    if payment_link:
        # Créer le QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_link)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64 pour l'affichage
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
    else:
        img_str = None
    
    return render(request, 'paiements/qr_code.html', {
        'paiement': paiement,
        'qr_code_image': img_str,
        'payment_link': payment_link
    })


@login_required
def paiement_verifier(request, paiement_id):
    """Vérifier le statut d'un paiement en attente"""
    if not request.user.is_etudiant:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement appartient à l'étudiant
    if paiement.etudiant.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    # Vérifier le statut via CinetPay
    try:
        service = CinetPayService()
    except (ValueError, Exception) as e:
        messages.error(request, f"Erreur de configuration: {str(e)}")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    result = service.verifier_paiement(paiement)
    
    if result.get('success'):
        if paiement.statut == StatutPaiement.SUCCESS:
            messages.success(request, "Votre paiement a été confirmé avec succès !")
            return redirect('paiements_templates:paiement_success', paiement_id=paiement.id)
        else:
            messages.info(request, f"Le statut du paiement est: {paiement.get_statut_display()}")
    else:
        messages.warning(request, f"Impossible de vérifier le paiement: {result.get('message', 'Erreur inconnue')}")
    
    return redirect('etudiants_templates:etudiant_dashboard')


@login_required
def paiement_receipt(request, paiement_id):
    """Télécharger le reçu PDF"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement appartient à l'utilisateur
    if request.user.is_etudiant and paiement.etudiant.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    if paiement.statut != StatutPaiement.SUCCESS:
        messages.error(request, "Ce paiement n'a pas été complété avec succès.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    # Générer le PDF
    pdf_buffer = generate_receipt_pdf(paiement)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_paiement_{paiement.id}.pdf"'
    
    return response


@login_required
def paiement_cancel(request, paiement_id):
    """Page d'annulation du paiement"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    # Vérifier que le paiement appartient à l'utilisateur
    if request.user.is_etudiant and paiement.etudiant.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    # Marquer le paiement comme annulé si ce n'est pas déjà fait
    if paiement.statut == StatutPaiement.PENDING:
        paiement.statut = StatutPaiement.CANCELLED
        paiement.message_erreur = "Paiement annulé par l'utilisateur"
        paiement.save()
        logger.info(f"Paiement {paiement.id} annulé par l'utilisateur")
    
    messages.info(request, "Le paiement a été annulé.")
    return render(request, 'paiements/cancel.html', {'paiement': paiement})

