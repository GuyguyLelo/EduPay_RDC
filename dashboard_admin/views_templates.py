"""
Vues templates pour le dashboard admin
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from core.permissions import IsSuperAdmin
from core.models import UserRole
from etablissements.models import Etablissement, StatutEtablissement
from paiements.models import Paiement, StatutPaiement
from etudiants.models import Etudiant


@login_required
def dashboard_overview(request):
    """Vue d'ensemble du dashboard"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    # Statistiques
    total_etablissements = Etablissement.objects.count()
    etablissements_actifs = Etablissement.objects.filter(statut=StatutEtablissement.ACTIF).count()
    total_etudiants = Etudiant.objects.count()
    total_paiements = Paiement.objects.count()
    
    revenus_totaux = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS
    ).aggregate(total=Sum('commission_plateforme'))['total'] or 0
    
    # Établissements récents
    etablissements_recents = Etablissement.objects.order_by('-date_inscription')[:5]
    
    # Paiements récents
    paiements_recents = Paiement.objects.select_related('etudiant').order_by('-date_creation')[:5]
    
    context = {
        'stats': {
            'total_etablissements': total_etablissements,
            'etablissements_actifs': etablissements_actifs,
            'total_etudiants': total_etudiants,
            'total_paiements': total_paiements,
            'revenus_totaux': revenus_totaux,
        },
        'etablissements_recents': etablissements_recents,
        'paiements_recents': paiements_recents,
    }
    
    return render(request, 'dashboard_admin/dashboard.html', context)


@login_required
def etablissements_list(request):
    """Liste des établissements"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from etablissements.forms import EtablissementForm
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    
    etablissements = Etablissement.objects.all().order_by('-date_inscription')
    form = EtablissementForm()
    
    if request.method == 'POST':
        form = EtablissementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                etablissement = form.save()
                messages.success(request, f'L\'établissement {etablissement.nom} a été créé avec succès.')
                logger.info(f"Établissement créé: {etablissement.nom} par {request.user.email}")
                return redirect('dashboard_admin_templates:dashboard_etablissements')
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'établissement: {str(e)}")
                messages.error(request, f'Une erreur est survenue lors de la création: {str(e)}')
        else:
            # Afficher les erreurs de validation
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire: ' + ', '.join(error_messages))
            logger.warning(f"Erreurs de validation: {form.errors}")
    
    return render(request, 'dashboard_admin/etablissements.html', {
        'etablissements': etablissements,
        'form': form
    })


@login_required
def paiements_list(request):
    """Liste des paiements"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    paiements = Paiement.objects.select_related('etudiant', 'frais', 'etudiant__etablissement').order_by('-date_creation')[:100]
    
    return render(request, 'dashboard_admin/paiements.html', {
        'paiements': paiements
    })


@login_required
def rapports_view(request):
    """Vue des rapports"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Statistiques du mois en cours
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    paiements_mois = Paiement.objects.filter(
        statut=StatutPaiement.SUCCESS,
        date_paiement__gte=debut_mois
    )
    
    revenus_mois = paiements_mois.aggregate(total=Sum('commission_plateforme'))['total'] or 0
    volume_mois = paiements_mois.aggregate(total=Sum('montant'))['total'] or 0
    
    return render(request, 'dashboard_admin/rapports.html', {
        'revenus_mois': revenus_mois,
        'volume_mois': volume_mois,
        'nombre_transactions': paiements_mois.count(),
    })


@login_required
def abonnements_list(request):
    """Liste des abonnements"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from abonnements.models import Abonnement
    
    abonnements = Abonnement.objects.select_related('etablissement').all().order_by('-date_creation')
    
    return render(request, 'dashboard_admin/abonnements.html', {
        'abonnements': abonnements
    })


@login_required
def activer_etablissement_view(request, etablissement_id):
    """Active un établissement (vue template)"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    
    etablissement = get_object_or_404(Etablissement, id=etablissement_id)
    etablissement.statut = StatutEtablissement.ACTIF
    etablissement.save()
    
    messages.success(request, f'L\'établissement {etablissement.nom} a été activé avec succès.')
    return redirect('dashboard_admin_templates:dashboard_etablissements')


@login_required
def suspendre_etablissement_view(request, etablissement_id):
    """Suspend un établissement (vue template)"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    
    etablissement = get_object_or_404(Etablissement, id=etablissement_id)
    etablissement.statut = StatutEtablissement.SUSPENDU
    etablissement.save()
    
    messages.success(request, f'L\'établissement {etablissement.nom} a été suspendu avec succès.')
    return redirect('dashboard_admin_templates:dashboard_etablissements')


@login_required
def etablissement_detail(request, etablissement_id):
    """Détails d'un établissement"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from etudiants.models import Etudiant
    from paiements.models import Paiement, StatutPaiement
    
    etablissement = get_object_or_404(Etablissement, id=etablissement_id)
    
    # Statistiques
    total_etudiants = Etudiant.objects.filter(etablissement=etablissement).count()
    total_paiements = Paiement.objects.filter(etudiant__etablissement=etablissement).count()
    paiements_reussis = Paiement.objects.filter(
        etudiant__etablissement=etablissement,
        statut=StatutPaiement.SUCCESS
    ).count()
    
    context = {
        'etablissement': etablissement,
        'total_etudiants': total_etudiants,
        'total_paiements': total_paiements,
        'paiements_reussis': paiements_reussis,
    }
    
    return render(request, 'dashboard_admin/etablissement_detail.html', context)


@login_required
def etablissement_edit(request, etablissement_id):
    """Modifier un établissement"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from etablissements.forms import EtablissementForm
    import logging
    
    logger = logging.getLogger(__name__)
    etablissement = get_object_or_404(Etablissement, id=etablissement_id)
    
    if request.method == 'POST':
        form = EtablissementForm(request.POST, request.FILES, instance=etablissement)
        if form.is_valid():
            try:
                etablissement = form.save()
                messages.success(request, f'L\'établissement {etablissement.nom} a été modifié avec succès.')
                logger.info(f"Établissement modifié: {etablissement.nom} par {request.user.email}")
                return redirect('dashboard_admin_templates:etablissement_detail', etablissement_id=etablissement.id)
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
    else:
        form = EtablissementForm(instance=etablissement)
    
    return render(request, 'dashboard_admin/etablissement_edit.html', {
        'etablissement': etablissement,
        'form': form
    })


@login_required
def paiement_detail(request, paiement_id):
    """Détails d'un paiement"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from paiements.models import Paiement
    
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    return render(request, 'dashboard_admin/paiement_detail.html', {
        'paiement': paiement
    })


@login_required
def abonnement_detail(request, abonnement_id):
    """Détails d'un abonnement"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404
    from abonnements.models import Abonnement
    
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    
    return render(request, 'dashboard_admin/abonnement_detail.html', {
        'abonnement': abonnement
    })


@login_required
def abonnement_edit(request, abonnement_id):
    """Modifier un abonnement"""
    if not request.user.is_super_admin:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from abonnements.models import Abonnement
    from django import forms
    import logging
    
    logger = logging.getLogger(__name__)
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    
    class AbonnementForm(forms.ModelForm):
        class Meta:
            model = Abonnement
            fields = ('type', 'statut', 'montant_mensuel', 'date_debut', 'date_fin')
            widgets = {
                'type': forms.Select(attrs={'class': 'form-select'}),
                'statut': forms.Select(attrs={'class': 'form-select'}),
                'montant_mensuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            }
    
    if request.method == 'POST':
        form = AbonnementForm(request.POST, instance=abonnement)
        if form.is_valid():
            try:
                abonnement = form.save()
                messages.success(request, f'L\'abonnement a été modifié avec succès.')
                logger.info(f"Abonnement modifié: {abonnement.id} par {request.user.email}")
                return redirect('dashboard_admin_templates:abonnement_detail', abonnement_id=abonnement.id)
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
    else:
        form = AbonnementForm(instance=abonnement)
    
    return render(request, 'dashboard_admin/abonnement_edit.html', {
        'abonnement': abonnement,
        'form': form
    })

