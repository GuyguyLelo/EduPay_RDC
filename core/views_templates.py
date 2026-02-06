"""
Vues pour les templates (non-API)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import User, UserRole
from .forms import UserRegistrationForm, UserLoginForm, PasswordChangeForm


def home_view(request):
    """Vue d'accueil"""
    return render(request, 'base.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion - Page par défaut"""
    if request.user.is_authenticated:
        # Rediriger selon le rôle
        if request.user.is_super_admin:
            return redirect('dashboard_admin_templates:dashboard_overview')
        elif request.user.is_etablissement_admin:
            return redirect('etablissements_templates:etablissement_dashboard')
        else:
            return redirect('etudiants_templates:etudiant_dashboard')
    
    form = UserLoginForm()
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Votre compte a été désactivé. Contactez l\'administrateur.')
                else:
                    login(request, user)
                    messages.success(request, f'Bienvenue {user.email} !')
                    # Rediriger selon le rôle
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
                    
                    if user.is_super_admin:
                        return redirect('dashboard_admin_templates:dashboard_overview')
                    elif user.is_etablissement_admin:
                        return redirect('etablissements_templates:etablissement_dashboard')
                    else:
                        return redirect('etudiants_templates:etudiant_dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    
    return render(request, 'registration/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('core_templates:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Inscription réussie ! Vous pouvez maintenant vous connecter.')
            return redirect('core_templates:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """Vue du tableau de bord principal"""
    # Rediriger selon le rôle de l'utilisateur
    if request.user.is_super_admin:
        return redirect('dashboard_admin_templates:dashboard_overview')
    elif request.user.is_etablissement_admin:
        return redirect('etablissements_templates:etablissement_dashboard')
    else:
        return redirect('etudiants_templates:etudiant_dashboard')


@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    return render(request, 'core/profile.html', {'user': request.user})


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core_templates:login')


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """Vue de changement de mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Mettre à jour la session pour éviter la déconnexion
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Votre mot de passe a été modifié avec succès !')
            return redirect('core_templates:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})

