"""
Vues templates pour les frais
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Frais
from .forms import FraisForm
import logging

logger = logging.getLogger(__name__)


@login_required
def frais_list(request):
    """Liste des frais"""
    if request.user.is_super_admin:
        frais_list = Frais.objects.select_related('etablissement').all()
    elif request.user.is_etablissement_admin:
        etablissement = request.user.etablissement_admin
        if etablissement:
            frais_list = Frais.objects.filter(etablissement=etablissement)
        else:
            frais_list = Frais.objects.none()
    elif request.user.is_etudiant:
        try:
            etudiant = request.user.etudiant
            frais_list = Frais.objects.filter(
                etablissement=etudiant.etablissement,
                actif=True
            )
        except:
            frais_list = Frais.objects.none()
    else:
        frais_list = Frais.objects.none()
    
    form = FraisForm(user=request.user)
    
    if request.method == 'POST':
        # Pour les admins d'établissement, ajouter l'établissement dans POST
        if request.user.is_etablissement_admin:
            etablissement = request.user.etablissement_admin
            if etablissement:
                # Créer une copie mutable de POST
                post_data = request.POST.copy()
                post_data['etablissement'] = etablissement.id
                form = FraisForm(post_data, user=request.user)
            else:
                messages.error(request, 'Aucun établissement associé à votre compte.')
                return render(request, 'frais/list.html', {
                    'frais_list': frais_list,
                    'form': FraisForm(user=request.user)
                })
        else:
            form = FraisForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                frais = form.save()
                messages.success(request, f'Les frais "{frais.nom_frais}" ont été créés avec succès.')
                logger.info(f"Frais créé: {frais.nom_frais} par {request.user.email}")
                return redirect('frais_templates:frais_list')
            except Exception as e:
                logger.error(f"Erreur lors de la création des frais: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, 'Veuillez corriger les erreurs: ' + ', '.join(error_messages))
    
    return render(request, 'frais/list.html', {
        'frais_list': frais_list,
        'form': form
    })


@login_required
def frais_detail(request, frais_id):
    """Détails d'un frais"""
    from django.shortcuts import get_object_or_404
    from paiements.models import Paiement, StatutPaiement
    
    frais = get_object_or_404(Frais, id=frais_id)
    
    # Vérifier les permissions
    if request.user.is_super_admin:
        pass  # Accès autorisé
    elif request.user.is_etablissement_admin:
        etablissement = request.user.etablissement_admin
        if not etablissement or frais.etablissement != etablissement:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Accès refusé")
    elif request.user.is_etudiant:
        etudiant = request.user.etudiant
        if not etudiant or frais.etablissement != etudiant.etablissement:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Accès refusé")
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    # Statistiques sur les paiements
    paiements = Paiement.objects.filter(frais=frais).order_by('-date_creation')
    paiements_reussis = paiements.filter(statut=StatutPaiement.SUCCESS).count()
    
    return render(request, 'frais/detail.html', {
        'frais': frais,
        'paiements': paiements,
        'paiements_reussis': paiements_reussis
    })


@login_required
def frais_edit(request, frais_id):
    """Modifier un frais"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    frais = get_object_or_404(Frais, id=frais_id)
    
    # Vérifier les permissions
    if request.user.is_super_admin:
        pass  # Accès autorisé
    elif request.user.is_etablissement_admin:
        etablissement = request.user.etablissement_admin
        if not etablissement or frais.etablissement != etablissement:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Accès refusé")
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès refusé")
    
    if request.method == 'POST':
        # Pour les admins d'établissement, ajouter l'établissement dans POST
        if request.user.is_etablissement_admin:
            etablissement = request.user.etablissement_admin
            if etablissement:
                post_data = request.POST.copy()
                post_data['etablissement'] = etablissement.id
                form = FraisForm(post_data, instance=frais, user=request.user)
            else:
                messages.error(request, 'Aucun établissement associé à votre compte.')
                return redirect('frais_templates:frais_detail', frais_id=frais.id)
        else:
            form = FraisForm(request.POST, instance=frais, user=request.user)
        
        if form.is_valid():
            try:
                frais = form.save()
                messages.success(request, f'Les frais "{frais.nom_frais}" ont été modifiés avec succès.')
                logger.info(f"Frais modifié: {frais.nom_frais} par {request.user.email}")
                return redirect('frais_templates:frais_detail', frais_id=frais.id)
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {str(e)}")
                messages.error(request, f'Une erreur est survenue: {str(e)}')
    else:
        form = FraisForm(instance=frais, user=request.user)
    
    return render(request, 'frais/edit.html', {
        'frais': frais,
        'form': form
    })

