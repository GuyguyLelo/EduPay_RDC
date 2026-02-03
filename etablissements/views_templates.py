"""
Vues templates pour les établissements
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import Etablissement
from etudiants.models import Etudiant
from paiements.models import Paiement, StatutPaiement


@login_required
def dashboard_etablissement(request):
    """Dashboard établissement"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    # Statistiques
    total_etudiants = Etudiant.objects.filter(etablissement=etablissement).count()
    paiements_reussis = Paiement.objects.filter(
        etudiant__etablissement=etablissement,
        statut=StatutPaiement.SUCCESS
    ).count()
    
    montant_total = Paiement.objects.filter(
        etudiant__etablissement=etablissement,
        statut=StatutPaiement.SUCCESS
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    paiements_en_attente = Paiement.objects.filter(
        etudiant__etablissement=etablissement,
        statut=StatutPaiement.PENDING
    ).count()
    
    # Données récentes
    etudiants_recents = Etudiant.objects.filter(
        etablissement=etablissement
    ).order_by('-date_inscription')[:5]
    
    paiements_recents = Paiement.objects.filter(
        etudiant__etablissement=etablissement
    ).select_related('etudiant').order_by('-date_creation')[:5]
    
    context = {
        'etablissement': etablissement,
        'stats': {
            'total_etudiants': total_etudiants,
            'paiements_reussis': paiements_reussis,
            'montant_total': montant_total,
            'paiements_en_attente': paiements_en_attente,
        },
        'etudiants_recents': etudiants_recents,
        'paiements_recents': paiements_recents,
    }
    
    return render(request, 'etablissements/dashboard.html', context)


@login_required
def etudiants_list(request):
    """Liste des étudiants de l'établissement"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from etudiants.forms import EtudiantForm
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    etudiants = Etudiant.objects.filter(etablissement=etablissement).order_by('-date_inscription')
    form = EtudiantForm(etablissement=etablissement)
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, etablissement=etablissement)
        if form.is_valid():
            try:
                etudiant = form.save()
                generated_password = getattr(form, 'generated_password', None)
                
                if generated_password:
                    messages.success(
                        request, 
                        f'L\'étudiant {etudiant.nom_complet} a été créé avec succès. '
                        f'Mot de passe généré: {generated_password} (à communiquer à l\'étudiant)'
                    )
                else:
                    messages.success(request, f'L\'étudiant {etudiant.nom_complet} a été créé avec succès.')
                
                logger.info(f"Étudiant créé: {etudiant.nom_complet} par {request.user.email}")
                return redirect('etablissements_templates:etablissement_etudiants')
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'étudiant: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Veuillez corriger les erreurs: ' + ', '.join(error_messages))
    
    return render(request, 'etablissements/etudiants.html', {
        'etablissement': etablissement,
        'etudiants': etudiants,
        'form': form
    })


@login_required
def paiements_list(request):
    """Liste des paiements de l'établissement"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    paiements = Paiement.objects.filter(
        etudiant__etablissement=etablissement
    ).select_related('etudiant', 'frais').order_by('-date_creation')
    
    return render(request, 'etablissements/paiements.html', {
        'etablissement': etablissement,
        'paiements': paiements
    })


@login_required
def comptes_paiement_list(request):
    """Liste des comptes Mobile Money de l'établissement"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from .models import ComptePaiement
    from .forms import ComptePaiementForm
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    comptes = ComptePaiement.objects.filter(etablissement=etablissement).order_by('-date_creation')
    form = ComptePaiementForm(etablissement=etablissement)
    
    if request.method == 'POST':
        form = ComptePaiementForm(request.POST, etablissement=etablissement)
        if form.is_valid():
            try:
                compte = form.save()
                messages.success(
                    request, 
                    f'Le compte {compte.get_operateur_display()} a été ajouté avec succès.'
                )
                logger.info(f"Compte Mobile Money créé: {compte.get_operateur_display()} par {request.user.email}")
                return redirect('etablissements_templates:etablissement_comptes')
            except Exception as e:
                logger.error(f"Erreur lors de la création du compte: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Veuillez corriger les erreurs: ' + ', '.join(error_messages))
    
    return render(request, 'etablissements/comptes.html', {
        'etablissement': etablissement,
        'comptes': comptes,
        'form': form
    })


@login_required
def etudiant_detail(request, etudiant_id):
    """Détails d'un étudiant"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from etudiants.models import Etudiant
    from paiements.models import Paiement
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    etudiant = get_object_or_404(Etudiant, id=etudiant_id, etablissement=etablissement)
    
    # Paiements de l'étudiant
    paiements = Paiement.objects.filter(etudiant=etudiant).order_by('-date_creation')
    
    return render(request, 'etablissements/etudiant_detail.html', {
        'etablissement': etablissement,
        'etudiant': etudiant,
        'paiements': paiements
    })


@login_required
def etudiant_edit(request, etudiant_id):
    """Modifier un étudiant"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from etudiants.models import Etudiant
    from etudiants.forms import EtudiantForm
    import logging
    
    logger = logging.getLogger(__name__)
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    etudiant = get_object_or_404(Etudiant, id=etudiant_id, etablissement=etablissement)
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, instance=etudiant, etablissement=etablissement)
        if form.is_valid():
            try:
                etudiant = form.save()
                messages.success(request, f'L\'étudiant {etudiant.nom_complet} a été modifié avec succès.')
                logger.info(f"Étudiant modifié: {etudiant.nom_complet} par {request.user.email}")
                return redirect('etablissements_templates:etudiant_detail', etudiant_id=etudiant.id)
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
    else:
        form = EtudiantForm(instance=etudiant, etablissement=etablissement)
        # Pré-remplir l'email
        if etudiant.user:
            form.fields['email'].initial = etudiant.user.email
    
    return render(request, 'etablissements/etudiant_edit.html', {
        'etablissement': etablissement,
        'etudiant': etudiant,
        'form': form
    })


@login_required
def paiement_detail(request, paiement_id):
    """Détails d'un paiement (établissement)"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from paiements.models import Paiement
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    paiement = get_object_or_404(
        Paiement, 
        id=paiement_id,
        etudiant__etablissement=etablissement
    )
    
    return render(request, 'etablissements/paiement_detail.html', {
        'etablissement': etablissement,
        'paiement': paiement
    })


@login_required
def compte_detail(request, compte_id):
    """Détails d'un compte Mobile Money"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from .models import ComptePaiement
    
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    compte = get_object_or_404(ComptePaiement, id=compte_id, etablissement=etablissement)
    
    return render(request, 'etablissements/compte_detail.html', {
        'etablissement': etablissement,
        'compte': compte
    })


@login_required
def compte_edit(request, compte_id):
    """Modifier un compte Mobile Money"""
    if not request.user.is_etablissement_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import ComptePaiement
    from .forms import ComptePaiementForm
    import logging
    
    logger = logging.getLogger(__name__)
    etablissement = request.user.etablissement_admin
    if not etablissement:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Aucun établissement associé")
    
    compte = get_object_or_404(ComptePaiement, id=compte_id, etablissement=etablissement)
    
    if request.method == 'POST':
        form = ComptePaiementForm(request.POST, instance=compte, etablissement=etablissement)
        if form.is_valid():
            try:
                compte = form.save()
                messages.success(request, f'Le compte a été modifié avec succès.')
                logger.info(f"Compte Mobile Money modifié: {compte.id} par {request.user.email}")
                return redirect('etablissements_templates:compte_detail', compte_id=compte.id)
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
    else:
        form = ComptePaiementForm(instance=compte, etablissement=etablissement)
    
    return render(request, 'etablissements/compte_edit.html', {
        'etablissement': etablissement,
        'compte': compte,
        'form': form
    })

