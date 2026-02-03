"""
Génération de reçus PDF pour les paiements
"""
import os
import logging
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .models import Paiement

logger = logging.getLogger(__name__)


def generate_receipt_pdf(paiement: Paiement) -> BytesIO:
    """
    Génère un reçu PDF pour un paiement
    
    Args:
        paiement: Instance du modèle Paiement
    
    Returns:
        BytesIO: Buffer contenant le PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # En-tête
    story.append(Paragraph("EDUPAY RDC", title_style))
    story.append(Paragraph("Reçu de Paiement", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Informations du paiement
    data = [
        ['Numéro de reçu:', f"REC-{paiement.id:06d}"],
        ['Date:', paiement.date_paiement.strftime('%d/%m/%Y %H:%M') if paiement.date_paiement else 'N/A'],
        ['Référence:', paiement.reference_flutterwave or 'N/A'],
        ['Transaction ID:', paiement.transaction_id or 'N/A'],
        ['', ''],
        ['ÉTUDIANT', ''],
        ['Nom complet:', paiement.etudiant.nom_complet],
        ['Matricule:', paiement.etudiant.matricule],
        ['Établissement:', paiement.etudiant.etablissement.nom],
        ['', ''],
        ['FRAIS', ''],
        ['Type de frais:', paiement.frais.nom_frais],
        ['Année académique:', paiement.frais.annee_academique],
        ['', ''],
        ['MONTANT', ''],
        ['Montant payé:', f"{paiement.montant:,.2f} {paiement.devise}"],
        ['Commission:', f"{paiement.commission_plateforme:,.2f} {paiement.devise}"],
        ['Montant net:', f"{paiement.montant_etablissement:,.2f} {paiement.devise}"],
    ]
    
    table = Table(data, colWidths=[3*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Message de confirmation
    message = Paragraph(
        "Ce document certifie que le paiement a été effectué avec succès via Mobile Money.",
        styles['Normal']
    )
    story.append(message)
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def send_payment_confirmation_sms(paiement: Paiement):
    """
    Envoie un SMS de confirmation de paiement via CinetPay SMS
    
    Args:
        paiement: Instance du modèle Paiement
    """
    try:
        from .sms_service import CinetPaySMSService
        
        sms_service = CinetPaySMSService()
        result = sms_service.envoyer_confirmation_paiement(paiement)
        
        if not result.get('success'):
            logger.warning(f"Échec de l'envoi du SMS pour le paiement {paiement.id}: {result.get('message')}")
        
        return result
    
    except ValueError as e:
        # Clé API SMS non configurée, on log mais on ne fait pas échouer le paiement
        logger.warning(f"Service SMS non disponible pour le paiement {paiement.id}: {str(e)}")
        return {'success': False, 'message': str(e)}
    
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du SMS pour le paiement {paiement.id}: {str(e)}")
        return {'success': False, 'message': str(e)}


def send_payment_confirmation_email(paiement: Paiement):
    """
    Envoie un email de confirmation avec le reçu PDF (fonction conservée pour compatibilité)
    
    Args:
        paiement: Instance du modèle Paiement
    """
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    
    # Générer le PDF
    pdf_buffer = generate_receipt_pdf(paiement)
    
    # Préparer l'email
    subject = f"Confirmation de paiement - {paiement.frais.nom_frais}"
    message = f"""
    Bonjour {paiement.etudiant.nom_complet},
    
    Votre paiement de {paiement.montant} {paiement.devise} pour {paiement.frais.nom_frais} 
    a été effectué avec succès.
    
    Référence: {paiement.reference_flutterwave}
    Date: {paiement.date_paiement.strftime('%d/%m/%Y %H:%M') if paiement.date_paiement else 'N/A'}
    
    Veuillez trouver ci-joint votre reçu de paiement.
    
    Cordialement,
    L'équipe EduPay RDC
    """
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[paiement.etudiant.user.email],
    )
    
    # Attacher le PDF
    email.attach(
        f'recu_paiement_{paiement.id}.pdf',
        pdf_buffer.getvalue(),
        'application/pdf'
    )
    
    try:
        email.send()
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email pour le paiement {paiement.id}: {str(e)}")

