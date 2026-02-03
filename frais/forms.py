"""
Formulaires pour l'app frais
"""
from django import forms
from .models import Frais, Devise
from etablissements.models import Etablissement


class FraisForm(forms.ModelForm):
    """Formulaire pour créer/modifier des frais"""
    
    class Meta:
        model = Frais
        fields = ('etablissement', 'nom_frais', 'montant', 'devise', 'annee_academique', 'description', 'actif')
        widgets = {
            'etablissement': forms.Select(attrs={
                'class': 'form-select',
            }),
            'nom_frais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Frais de scolarité, Frais d\'inscription...'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'devise': forms.Select(attrs={
                'class': 'form-select',
            }),
            'annee_academique': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2024-2025'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description optionnelle des frais'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'etablissement': 'Établissement',
            'nom_frais': 'Nom des frais',
            'montant': 'Montant',
            'devise': 'Devise',
            'annee_academique': 'Année académique',
            'description': 'Description',
            'actif': 'Actif',
        }
    
    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec l'établissement de l'utilisateur si admin établissement"""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si l'utilisateur est admin d'établissement, limiter les choix
        if user and user.is_etablissement_admin:
            etablissement = user.etablissement_admin
            if etablissement:
                self.fields['etablissement'].queryset = Etablissement.objects.filter(id=etablissement.id)
                self.fields['etablissement'].initial = etablissement.id
                # Rendre le champ non modifiable
                self.fields['etablissement'].widget.attrs['readonly'] = True
                self.fields['etablissement'].widget.attrs['disabled'] = True
                self.fields['etablissement'].widget.attrs['class'] = 'form-select'
                # Stocker l'établissement pour l'affichage
                self.etablissement_display = etablissement
        elif user and not user.is_super_admin:
            # Cacher le champ établissement pour les non-super-admin
            self.fields['etablissement'].widget = forms.HiddenInput()
        else:
            self.etablissement_display = None
    
    def clean_montant(self):
        """Valide que le montant est positif"""
        montant = self.cleaned_data.get('montant')
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant
    
    def clean_annee_academique(self):
        """Valide le format de l'année académique"""
        annee = self.cleaned_data.get('annee_academique')
        if annee:
            # Format attendu: YYYY-YYYY ou YYYY/YYYY
            annee = annee.strip()
        return annee

