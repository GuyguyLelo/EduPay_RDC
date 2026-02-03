"""
Vues templates pour les paiements
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from frais.models import Frais
from .models import Paiement, StatutPaiement
from .services_cinetpay import CinetPayService
from .receipts import generate_receipt_pdf

logger = logging.getLogger(__name__)


@login_required
def payer_frais(request, frais_id):
    """Page de paiement d'un frais"""
    if not request.user.is_etudiant:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    frais = get_object_or_404(Frais, id=frais_id, actif=True)
    etudiant = request.user.etudiant
    
    # Vérifier si le frais appartient à l'établissement de l'étudiant
    if frais.etablissement != etudiant.etablissement:
        messages.error(request, "Ce frais ne vous concerne pas.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    # Vérifier si déjà payé
    paiement_existant = Paiement.objects.filter(
        etudiant=etudiant,
        frais=frais,
        statut=StatutPaiement.SUCCESS
    ).first()
    
    if paiement_existant:
        messages.info(request, "Ce frais a déjà été payé.")
        return redirect('etudiants_templates:etudiant_dashboard')
    
    if request.method == 'POST':
        methode_paiement = request.POST.get('methode_paiement', 'MOBILE_MONEY')
        
        # Créer le paiement
        from django.conf import settings
        from decimal import Decimal
        from .models import MethodePaiement
        
        paiement = Paiement.objects.create(
            etudiant=etudiant,
            frais=frais,
            montant=frais.montant,
            devise=frais.devise,
            methode_paiement=methode_paiement,
            statut=StatutPaiement.PENDING,
            taux_commission=settings.COMMISSION_RATE
        )
        
        # Initier le paiement selon la méthode choisie
        try:
            # Utiliser CinetPay
            try:
                service = CinetPayService()
            except (ValueError, Exception) as e:
                logger.error(f"Erreur lors de l'initialisation de CinetPay: {e}")
                messages.error(request, "Aucune passerelle de paiement configurée. Veuillez configurer CinetPay dans .env")
                return redirect('etudiants_templates:etudiant_dashboard')
            
            if methode_paiement == MethodePaiement.CARTE_BANCAIRE:
                # Paiement par carte bancaire (plus rapide)
                email = request.POST.get('email', etudiant.user.email)
                result = service.initier_paiement_carte_bancaire(
                    paiement=paiement,
                    email=email
                )
                
                if result.get('success'):
                    # Rediriger vers la page de paiement
                    payment_link = result.get('payment_link')
                    if payment_link:
                        return redirect(payment_link)
                    else:
                        messages.success(request, "Paiement par carte initié avec succès.")
                        return redirect('paiements_templates:paiement_success', paiement_id=paiement.id)
                else:
                    messages.error(request, f"Erreur: {result.get('message', 'Erreur inconnue')}")
            
            elif methode_paiement == MethodePaiement.QR_CODE:
                # Paiement par QR Code (très rapide)
                email = request.POST.get('email', etudiant.user.email)
                result = service.initier_paiement_qr_code(
                    paiement=paiement,
                    email=email
                )
                
                if result.get('success'):
                    # Rediriger vers la page d'affichage du QR Code
                    return redirect('paiements_templates:paiement_qr_code', paiement_id=paiement.id)
                else:
                    messages.error(request, f"Erreur: {result.get('message', 'Erreur inconnue')}")
            
            else:
                # Paiement Mobile Money (méthode traditionnelle)
                numero_telephone = request.POST.get('numero_telephone')
                operateur = request.POST.get('operateur')
                
                paiement.numero_telephone = numero_telephone
                paiement.operateur = operateur
                paiement.save()
                
                result = service.initier_paiement_mobile_money(
                    paiement=paiement,
                    numero_telephone=numero_telephone,
                    operateur=operateur
                )
                
                if result.get('success'):
                    messages.success(request, "Paiement initié avec succès. Veuillez confirmer sur votre téléphone.")
                    return redirect('paiements_templates:paiement_success', paiement_id=paiement.id)
                else:
                    error_message = result.get('message', 'Erreur inconnue')
                    # Si c'est un problème d'opérateur, afficher un message spécial
                    if result.get('retry_possible'):
                        messages.warning(request, error_message)
                        # Rediriger vers la page de paiement pour permettre un nouvel essai
                        return redirect('paiements_templates:payer_frais', frais_id=frais.id)
                    else:
                        messages.error(request, f"Erreur: {error_message}")
                    
        except ValueError as e:
            # Erreur de configuration CinetPay
            messages.error(request, f"Configuration manquante: {str(e)}")
            logger.error(f"Erreur de configuration CinetPay: {str(e)}")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de l'initiation du paiement: {str(e)}")
            logger.exception(f"Erreur lors de l'initiation du paiement {paiement.id}: {str(e)}")
    
    # Récupérer les messages d'erreur pour les afficher dans le template
    error_messages = messages.get_messages(request)
    has_operator_error = any('opérateur' in str(msg).lower() or 'operator' in str(msg).lower() for msg in error_messages)
    
    return render(request, 'paiements/payer.html', {
        'frais': frais,
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

