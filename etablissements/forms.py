"""
Formulaires pour l'app etablissements
"""
from django import forms
from .models import Etablissement, ComptePaiement, TypeEtablissement, OperateurMobileMoney
from core.models import User, UserRole


class EtablissementForm(forms.ModelForm):
    """Formulaire pour créer/modifier un établissement"""
    
    # Champs pour créer l'administrateur
    admin_email = forms.EmailField(
        required=False,
        label='Email de l\'administrateur',
        help_text='Si fourni, un compte administrateur sera créé pour cet établissement'
    )
    admin_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Mot de passe administrateur',
        help_text='Minimum 8 caractères'
    )
    
    class Meta:
        model = Etablissement
        fields = ('nom', 'type', 'email', 'telephone', 'adresse', 'logo')
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Université de Kinshasa'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@etablissement.cd'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243900000000'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète de l\'établissement'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'nom': 'Nom de l\'établissement',
            'type': 'Type d\'établissement',
            'email': 'Email de contact',
            'telephone': 'Téléphone',
            'adresse': 'Adresse',
            'logo': 'Logo (optionnel)',
        }
    
    def clean_telephone(self):
        """Valide le format du téléphone"""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Nettoyer le numéro de téléphone
            telephone = telephone.strip().replace(' ', '').replace('-', '')
            
            # Si le numéro commence par 0, le remplacer par +243
            if telephone.startswith('0'):
                telephone = '+243' + telephone[1:]
            # Si le numéro commence par 243, ajouter +
            elif telephone.startswith('243'):
                telephone = '+' + telephone
            # Si le numéro ne commence pas par +, l'ajouter
            elif not telephone.startswith('+'):
                # Vérifier si c'est un numéro valide
                if telephone.isdigit():
                    telephone = '+243' + telephone.lstrip('0')
                else:
                    telephone = '+' + telephone
            
            # Vérifier que le format final est valide (au moins 9 chiffres après le +)
            if not telephone.startswith('+') or len([c for c in telephone if c.isdigit()]) < 9:
                raise forms.ValidationError("Format de téléphone invalide. Utilisez le format: +243XXXXXXXXX")
        
        return telephone
    
    def clean_admin_password(self):
        """Valide le mot de passe admin si email fourni"""
        admin_email = self.cleaned_data.get('admin_email')
        admin_password = self.cleaned_data.get('admin_password')
        
        if admin_email and not admin_password:
            raise forms.ValidationError("Le mot de passe est requis si un email administrateur est fourni.")
        
        if admin_password and len(admin_password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        return admin_password
    
    def save(self, commit=True):
        """Sauvegarde l'établissement et crée l'admin si nécessaire"""
        etablissement = super().save(commit=False)
        
        if commit:
            etablissement.save()
            
            # Créer l'administrateur si email fourni
            admin_email = self.cleaned_data.get('admin_email')
            admin_password = self.cleaned_data.get('admin_password')
            
            if admin_email and admin_password:
                # Vérifier si l'utilisateur existe déjà
                if not User.objects.filter(email=admin_email).exists():
                    admin_user = User.objects.create_user(
                        email=admin_email,
                        password=admin_password,
                        role=UserRole.ETABLISSEMENT_ADMIN
                    )
                    etablissement.admin = admin_user
                    etablissement.save()
                else:
                    # Utiliser l'utilisateur existant
                    admin_user = User.objects.get(email=admin_email)
                    if admin_user.role != UserRole.ETABLISSEMENT_ADMIN:
                        admin_user.role = UserRole.ETABLISSEMENT_ADMIN
                        admin_user.save()
                    etablissement.admin = admin_user
                    etablissement.save()
        
        return etablissement


class ComptePaiementForm(forms.ModelForm):
    """Formulaire pour ajouter un compte de paiement"""
    
    class Meta:
        model = ComptePaiement
        fields = ('intitule', 'operateur', 'numero_compte', 'actif')
        widgets = {
            'intitule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Compte principal, Compte Orange Money'
            }),
            'operateur': forms.Select(attrs={
                'class': 'form-select',
            }),
            'numero_compte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +243900000000'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'intitule': 'Intitulé du compte',
            'operateur': 'Opérateur Mobile Money',
            'numero_compte': 'Numéro de compte',
            'actif': 'Actif',
        }
    
    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec l'établissement"""
        etablissement = kwargs.pop('etablissement', None)
        super().__init__(*args, **kwargs)
        self.etablissement = etablissement
        
        # Personnaliser les choix d'opérateurs
        self.fields['operateur'].choices = OperateurMobileMoney.choices
    
    def clean_numero_compte(self):
        """Valide le format du numéro de compte"""
        numero = self.cleaned_data.get('numero_compte')
        if numero:
            numero = numero.strip().replace(' ', '').replace('-', '')
        return numero
    
    def clean(self):
        """Valide l'unicité opérateur/établissement"""
        cleaned_data = super().clean()
        operateur = cleaned_data.get('operateur')
        
        if self.etablissement and operateur:
            # Vérifier si un compte existe déjà pour cet opérateur
            existing = ComptePaiement.objects.filter(
                etablissement=self.etablissement,
                operateur=operateur
            )
            
            # Exclure l'instance actuelle si on est en mode édition
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                operateur_display = dict(OperateurMobileMoney.choices).get(operateur, operateur)
                raise forms.ValidationError(
                    f"Un compte {operateur_display} existe déjà pour cet établissement."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Sauvegarde le compte de paiement"""
        compte = super().save(commit=False)
        
        if not self.etablissement:
            raise ValueError("L'établissement doit être défini")
        
        compte.etablissement = self.etablissement
        
        if commit:
            compte.save()
        
        return compte

