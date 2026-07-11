"""
Views pour la gestion des paiements
"""
import logging
from django.utils import timezone
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .models import Paiement, StatutPaiement
from .serializers import PaiementSerializer, PaiementCreateSerializer, WebhookSerializer
from .services_cinetpay import CinetPayService
from .utils import calculer_commission
from .receipts import generate_receipt_pdf, send_payment_confirmation_sms
from core.permissions import IsEtudiant, IsOwnerOrReadOnly
from django.conf import settings

logger = logging.getLogger(__name__)


class PaiementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des paiements"""
    queryset = Paiement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PaiementSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaiementCreateSerializer
        return PaiementSerializer
    
    def get_queryset(self):
        """Filtre les paiements selon le rôle de l'utilisateur"""
        user = self.request.user
        
        if user.is_super_admin:
            return Paiement.objects.all()
        elif user.is_etablissement_admin:
            # Paiements des étudiants de son établissement
            etablissement = user.etablissement_admin
            if etablissement:
                return Paiement.objects.filter(etudiant__etablissement=etablissement)
        elif user.is_etudiant:
            # Paiements de l'étudiant connecté
            if hasattr(user, 'etudiant'):
                return Paiement.objects.filter(etudiant=user.etudiant)
        
        return Paiement.objects.none()
    
    def perform_create(self, serializer):
        """Crée un paiement et initie le processus de paiement"""
        paiement = serializer.save()
        
        # Utiliser CinetPay
        service = CinetPayService()
        
        result = service.initier_paiement_mobile_money(
            paiement=paiement,
            numero_telephone=serializer.validated_data['numero_telephone'],
            operateur=serializer.validated_data['operateur']
        )
        
        if not result.get('success'):
            logger.error(f"Échec de l'initiation du paiement {paiement.id}: {result.get('message')}")
            # Le paiement reste en PENDING, l'utilisateur peut réessayer
    
    @action(detail=True, methods=['post'])
    def verifier(self, request, pk=None):
        """Vérifie le statut d'un paiement"""
        paiement = self.get_object()
        
        # Utiliser CinetPay
        service = CinetPayService()
        
        if paiement.transaction_id:
            result = service.verifier_statut_paiement(paiement.transaction_id)
            
            if result.get('success'):
                if paiement.statut == StatutPaiement.SUCCESS:
                    # Envoyer le SMS de confirmation
                    send_payment_confirmation_sms(paiement)
                
                return Response({
                    'statut': paiement.statut,
                    'message': 'Paiement vérifié avec succès'
                })
            else:
                return Response(
                    {'error': result.get('message', 'Erreur lors de la vérification')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Aucune transaction associée à ce paiement'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([])  # Pas de permission requise pour les webhooks
@csrf_exempt
def webhook_cinetpay(request):
    """
    Webhook pour recevoir les notifications de CinetPay
    """
    try:
        payload = request.data
        logger.info(f"Webhook CinetPay reçu: {payload}")
        
        # Valider le webhook
        try:
            service = CinetPayService()
            logger.info("Service CinetPay initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur d'initialisation CinetPay: {e}")
            return Response(
                {'error': f'Erreur de configuration: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Traiter le webhook
        transaction_id = payload.get('cpm_trans_id') or payload.get('transaction_id')
        status_payment = payload.get('status', '').upper()
        
        logger.info(f"Transaction ID: {transaction_id}, Status: {status_payment}")
        
        if transaction_id:
            # Trouver le paiement
            try:
                paiement = Paiement.objects.get(transaction_id=transaction_id)
                logger.info(f"Paiement trouvé: {paiement.id}")
                
                if status_payment == 'ACCEPTED' or status_payment == 'SUCCESS':
                    paiement.statut = StatutPaiement.SUCCESS
                    paiement.date_paiement = timezone.now()
                    paiement.save()
                    
                    logger.info(f"Paiement {paiement.id} confirmé via webhook CinetPay")
                    
                    # Envoyer le SMS de confirmation
                    try:
                        send_payment_confirmation_sms(paiement)
                        logger.info(f"SMS de confirmation envoyé pour le paiement {paiement.id}")
                    except Exception as sms_error:
                        logger.error(f"Erreur lors de l'envoi du SMS: {sms_error}")
                
                elif status_payment == 'REFUSED' or status_payment == 'FAILED':
                    paiement.statut = StatutPaiement.FAILED
                    paiement.message_erreur = payload.get('message', 'Paiement refusé')
                    paiement.save()
                    
                    logger.info(f"Paiement {paiement.id} échoué via webhook CinetPay")
            
            except Paiement.DoesNotExist:
                logger.warning(f"Paiement non trouvé pour transaction_id: {transaction_id}")
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Erreur générale dans le webhook CinetPay: {e}")
        return Response(
            {'error': f'Erreur serveur: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    except Exception as e:
        logger.exception(f"Erreur lors du traitement du webhook CinetPay: {str(e)}")
        return Response(
            {'error': 'Erreur lors du traitement du webhook'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

