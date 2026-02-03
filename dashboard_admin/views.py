"""
Vues pour le dashboard super administrateur
"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperAdmin
from etablissements.models import Etablissement, StatutEtablissement
from paiements.models import Paiement, StatutPaiement
from etudiants.models import Etudiant
from abonnements.models import Abonnement


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def dashboard_overview(request):
    """
    Vue d'ensemble du dashboard super admin
    """
    # Statistiques générales
    total_etablissements = Etablissement.objects.count()
    etablissements_actifs = Etablissement.objects.filter(statut=StatutEtablissement.ACTIF).count()
    total_etudiants = Etudiant.objects.count()
    total_paiements = Paiement.objects.count()
    
    # Paiements réussis
    paiements_reussis = Paiement.objects.filter(statut=StatutPaiement.SUCCESS).count()
    
    # Revenus de la plateforme
    revenus_totaux = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS
    ).aggregate(total=Sum('commission_plateforme'))['total'] or 0
    
    # Revenus du mois en cours
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenus_mois = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS,
        date_paiement__gte=debut_mois
    ).aggregate(total=Sum('commission_plateforme'))['total'] or 0
    
    # Volume de transactions du mois
    volume_mois = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS,
        date_paiement__gte=debut_mois
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    return Response({
        'statistiques': {
            'total_etablissements': total_etablissements,
            'etablissements_actifs': etablissements_actifs,
            'total_etudiants': total_etudiants,
            'total_paiements': total_paiements,
            'paiements_reussis': paiements_reussis,
            'taux_reussite': round((paiements_reussis / total_paiements * 100) if total_paiements > 0 else 0, 2),
        },
        'revenus': {
            'totaux': float(revenus_totaux),
            'mois_courant': float(revenus_mois),
            'volume_mois': float(volume_mois),
        }
    })


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def etablissements_list(request):
    """
    Liste tous les établissements avec leurs statistiques
    """
    etablissements = Etablissement.objects.annotate(
        nombre_etudiants=Count('etudiants'),
        nombre_paiements=Count('etudiants__paiements'),
        revenus_generes=Sum('etudiants__paiements__commission_plateforme',
                          filter=Q(etudiants__paiements__statut=StatutPaiement.SUCCESS))
    ).order_by('-date_inscription')
    
    data = []
    for etab in etablissements:
        data.append({
            'id': etab.id,
            'nom': etab.nom,
            'type': etab.get_type_display(),
            'statut': etab.get_statut_display(),
            'email': etab.email,
            'telephone': etab.telephone,
            'date_inscription': etab.date_inscription,
            'nombre_etudiants': etab.nombre_etudiants,
            'nombre_paiements': etab.nombre_paiements,
            'revenus_generes': float(etab.revenus_generes or 0),
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def activer_etablissement(request, etablissement_id):
    """
    Active un établissement
    """
    try:
        etablissement = Etablissement.objects.get(id=etablissement_id)
        etablissement.statut = StatutEtablissement.ACTIF
        etablissement.save()
        return Response({'message': 'Établissement activé avec succès'})
    except Etablissement.DoesNotExist:
        return Response(
            {'error': 'Établissement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def suspendre_etablissement(request, etablissement_id):
    """
    Suspend un établissement
    """
    try:
        etablissement = Etablissement.objects.get(id=etablissement_id)
        etablissement.statut = StatutEtablissement.SUSPENDU
        etablissement.save()
        return Response({'message': 'Établissement suspendu avec succès'})
    except Etablissement.DoesNotExist:
        return Response(
            {'error': 'Établissement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def paiements_list(request):
    """
    Liste tous les paiements avec filtres
    """
    statut = request.query_params.get('statut')
    etablissement_id = request.query_params.get('etablissement_id')
    date_debut = request.query_params.get('date_debut')
    date_fin = request.query_params.get('date_fin')
    
    queryset = Paiement.objects.select_related('etudiant', 'frais', 'etudiant__etablissement').all()
    
    if statut:
        queryset = queryset.filter(statut=statut)
    
    if etablissement_id:
        queryset = queryset.filter(etudiant__etablissement_id=etablissement_id)
    
    if date_debut:
        queryset = queryset.filter(date_paiement__gte=date_debut)
    
    if date_fin:
        queryset = queryset.filter(date_paiement__lte=date_fin)
    
    paiements = queryset.order_by('-date_creation')[:100]  # Limiter à 100 résultats
    
    data = []
    for paiement in paiements:
        data.append({
            'id': paiement.id,
            'etudiant': paiement.etudiant.nom_complet,
            'matricule': paiement.etudiant.matricule,
            'etablissement': paiement.etudiant.etablissement.nom,
            'frais': paiement.frais.nom_frais,
            'montant': float(paiement.montant),
            'devise': paiement.devise,
            'statut': paiement.get_statut_display(),
            'commission': float(paiement.commission_plateforme),
            'date_paiement': paiement.date_paiement,
            'reference': paiement.reference_flutterwave,
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def rapports_mensuels(request):
    """
    Génère des rapports mensuels des revenus
    """
    mois = request.query_params.get('mois', timezone.now().month)
    annee = request.query_params.get('annee', timezone.now().year)
    
    debut_mois = timezone.now().replace(year=annee, month=mois, day=1, hour=0, minute=0, second=0, microsecond=0)
    if mois == 12:
        fin_mois = timezone.now().replace(year=annee + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fin_mois = timezone.now().replace(year=annee, month=mois + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    paiements = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS,
        date_paiement__gte=debut_mois,
        date_paiement__lt=fin_mois
    )
    
    revenus = paiements.aggregate(total=Sum('commission_plateforme'))['total'] or 0
    volume = paiements.aggregate(total=Sum('montant'))['total'] or 0
    nombre_transactions = paiements.count()
    
    # Par établissement
    par_etablissement = paiements.values('etudiant__etablissement__nom').annotate(
        revenus=Sum('commission_plateforme'),
        volume=Sum('montant'),
        nombre=Count('id')
    ).order_by('-revenus')
    
    return Response({
        'periode': {
            'mois': mois,
            'annee': annee,
            'debut': debut_mois,
            'fin': fin_mois,
        },
        'resume': {
            'revenus': float(revenus),
            'volume': float(volume),
            'nombre_transactions': nombre_transactions,
        },
        'par_etablissement': list(par_etablissement),
    })


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def abonnements_list(request):
    """
    Liste tous les abonnements
    """
    abonnements = Abonnement.objects.select_related('etablissement').all()
    
    data = []
    for abo in abonnements:
        data.append({
            'id': abo.id,
            'etablissement': abo.etablissement.nom,
            'type': abo.get_type_display(),
            'statut': abo.get_statut_display(),
            'montant_mensuel': float(abo.montant_mensuel),
            'date_debut': abo.date_debut,
            'date_fin': abo.date_fin,
            'is_actif': abo.is_actif,
        })
    
    return Response(data)
