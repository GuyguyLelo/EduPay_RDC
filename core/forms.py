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





