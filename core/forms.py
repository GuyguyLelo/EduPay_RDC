"""
Formulaires pour l'app core
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole


class UserRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Mot de passe',
        validators=[validate_password]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmer le mot de passe'
    )
    role = forms.ChoiceField(
        choices=[
            ('', 'Sélectionner...'),
            (UserRole.ETUDIANT, 'Étudiant'),
            (UserRole.ETABLISSEMENT_ADMIN, 'Administrateur d\'établissement'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type de compte'
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """Formulaire de connexion"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Mot de passe'
    )


class PasswordChangeForm(forms.Form):
    """Formulaire de changement de mot de passe"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe actuel'
        }),
        label='Mot de passe actuel',
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe'
        }),
        label='Nouveau mot de passe',
        required=True,
        validators=[validate_password],
        help_text='Le mot de passe doit contenir au moins 8 caractères.'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre nouveau mot de passe'
        }),
        label='Confirmer le nouveau mot de passe',
        required=True
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        """Vérifie que l'ancien mot de passe est correct"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return old_password
    
    def clean(self):
        """Vérifie que les nouveaux mots de passe correspondent"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password and new_password2:
            if new_password != new_password2:
                raise forms.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
            
            # Vérifier que le nouveau mot de passe est différent de l'ancien
            if self.user.check_password(new_password):
                raise forms.ValidationError("Le nouveau mot de passe doit être différent de l'ancien.")
        
        return cleaned_data
    
    def save(self):
        """Sauvegarde le nouveau mot de passe"""
        password = self.cleaned_data['new_password']
        self.user.set_password(password)
        self.user.save()
        return self.user





