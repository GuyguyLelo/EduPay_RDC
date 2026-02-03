"""
Vues templates pour les étudiants
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Etudiant
from frais.models import Frais
from paiements.models import Paiement, StatutPaiement


@login_required
def dashboard_etudiant(request):
    """Dashboard étudiant"""
    if not request.user.is_etudiant:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    try:
        etudiant = request.user.etudiant
    except Etudiant.DoesNotExist:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Profil étudiant non trouvé")
    
    # Frais à payer (frais actifs sans paiement réussi)
    frais_payes = Paiement.objects.filter(
        etudiant=etudiant,
        statut=StatutPaiement.SUCCESS
    ).values_list('frais_id', flat=True)
    
    frais_a_payer = Frais.objects.filter(
        etablissement=etudiant.etablissement,
        actif=True
    ).exclude(id__in=frais_payes)
    
    # Paiements
    paiements = Paiement.objects.filter(etudiant=etudiant).order_by('-date_creation')[:10]
    paiements_reussis = Paiement.objects.filter(
        etudiant=etudiant,
        statut=StatutPaiement.SUCCESS
    ).count()
    
    context = {
        'etudiant': etudiant,
        'frais_a_payer': frais_a_payer,
        'paiements': paiements,
        'paiements_reussis': paiements_reussis,
    }
    
    return render(request, 'etudiants/dashboard.html', context)





