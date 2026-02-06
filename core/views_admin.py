"""
Vues administratives temporaires pour Render
"""
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
import os

User = get_user_model()

def create_superuser_view(request):
    """Vue temporaire pour créer un superutilisateur sur Render"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email et mot de passe sont requis.')
            return render(request, 'admin/create_superuser.html')
        
        if password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'admin/create_superuser.html')
        
        if len(password) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
            return render(request, 'admin/create_superuser.html')
        
        try:
            with transaction.atomic():
                # Vérifier si l'utilisateur existe déjà
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    # Mettre à jour le mot de passe si l'utilisateur existe
                    user.set_password(password)
                    user.is_super_admin = True
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    messages.success(request, f'Superutilisateur {email} mis à jour avec succès !')
                else:
                    # Créer le superutilisateur
                    user = User.objects.create_superuser(
                        email=email,
                        password=password,
                        first_name=request.POST.get('first_name', '').strip(),
                        last_name=request.POST.get('last_name', '').strip(),
                        phone=request.POST.get('phone', '').strip(),
                        is_active=True,
                        is_verified=True
                    )
                    messages.success(request, f'Superutilisateur {email} créé avec succès !')
                
                return redirect('core_templates:login')
                
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            return render(request, 'admin/create_superuser.html')
    
    return render(request, 'admin/create_superuser.html')

def setup_etablissement_view(request):
    """Vue pour configurer un établissement pour le superutilisateur"""
    if not request.user.is_authenticated or not request.user.is_super_admin:
        messages.error(request, 'Accès non autorisé.')
        return redirect('core_templates:login')
    
    if request.method == 'POST':
        from etablissements.models import Etablissement, EtablissementAdmin
        
        nom = request.POST.get('nom', '').strip()
        type_etablissement = request.POST.get('type_etablissement', 'primaire')
        ville = request.POST.get('ville', '').strip()
        province = request.POST.get('province', '').strip()
        
        if not nom:
            messages.error(request, 'Le nom de l\'établissement est requis.')
            return render(request, 'admin/setup_etablissement.html')
        
        try:
            with transaction.atomic():
                # Créer l'établissement
                etablissement = Etablissement.objects.create(
                    nom=nom,
                    type_etablissement=type_etablissement,
                    ville=ville,
                    province=province,
                    statut='actif',
                    created_by=request.user
                )
                
                # Associer l'utilisateur comme admin
                EtablissementAdmin.objects.create(
                    user=request.user,
                    etablissement=etablissement,
                    role='admin_principal',
                    statut='actif'
                )
                
                messages.success(request, f'Établissement "{nom}" créé et associé à votre compte !')
                return redirect('etablissements_templates:etablissement_dashboard')
                
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            return render(request, 'admin/setup_etablissement.html')
    
    return render(request, 'admin/setup_etablissement.html')

def quick_setup_view(request):
    """Vue pour configuration rapide complète"""
    if request.method == 'POST':
        # Étape 1: Créer le superutilisateur
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        nom_etablissement = request.POST.get('nom_etablissement', '').strip()
        
        if not email or not password or not nom_etablissement:
            messages.error(request, 'Tous les champs sont requis.')
            return render(request, 'admin/quick_setup.html')
        
        try:
            with transaction.atomic():
                # Créer ou mettre à jour le superutilisateur
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.is_super_admin = True
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    messages.success(request, f'Superutilisateur {email} mis à jour !')
                else:
                    user = User.objects.create_superuser(
                        email=email,
                        password=password,
                        first_name='Admin',
                        last_name='EduPay',
                        is_active=True,
                        is_verified=True
                    )
                    messages.success(request, f'Superutilisateur {email} créé !')
                
                # Créer l'établissement
                from etablissements.models import Etablissement, EtablissementAdmin
                
                etablissement = Etablissement.objects.create(
                    nom=nom_etablissement,
                    type_etablissement='primaire',
                    ville='Kinshasa',
                    province='Kinshasa',
                    statut='actif',
                    created_by=user
                )
                
                # Associer l'utilisateur comme admin
                EtablissementAdmin.objects.create(
                    user=user,
                    etablissement=etablissement,
                    role='admin_principal',
                    statut='actif'
                )
                
                messages.success(request, 'Configuration terminée ! Vous pouvez maintenant vous connecter.')
                return redirect('core_templates:login')
                
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return render(request, 'admin/quick_setup.html')
    
    return render(request, 'admin/quick_setup.html')

def debug_users_view(request):
    """Vue de débogage pour voir les utilisateurs"""
    users = User.objects.all()
    user_info = []
    
    for user in users:
        user_info.append({
            'email': user.email,
            'is_super_admin': getattr(user, 'is_super_admin', False),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'is_verified': getattr(user, 'is_verified', False),
            'etablissements': [ea.etablissement.nom for ea in user.etablissementadmin_set.all()]
        })
    
    return JsonResponse({'users': user_info})

def force_login_view(request):
    """Vue pour forcer la connexion (temporaire pour débogage)"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email et mot de passe sont requis.')
            return render(request, 'admin/force_login.html')
        
        try:
            # Vérifier si l'utilisateur existe
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                
                # Mettre à jour le mot de passe
                user.set_password(password)
                user.is_active = True
                user.is_verified = True
                user.save()
                
                # Authentifier l'utilisateur
                authenticated_user = authenticate(request, username=email, password=password)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    messages.success(request, f'Connexion réussie pour {email} !')
                    
                    # Rediriger selon le rôle
                    if user.is_super_admin:
                        return redirect('dashboard_admin_templates:dashboard_overview')
                    elif hasattr(user, 'is_etablissement_admin') and user.is_etablissement_admin:
                        return redirect('etablissements_templates:etablissement_dashboard')
                    else:
                        return redirect('etudiants_templates:etudiant_dashboard')
                else:
                    messages.error(request, 'Échec de l\'authentification après mise à jour.')
            else:
                messages.error(request, f'Utilisateur {email} non trouvé.')
                
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    return render(request, 'admin/force_login.html')
