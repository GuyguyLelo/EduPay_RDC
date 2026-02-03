"""
Formulaires pour l'app etudiants
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Etudiant
from core.models import User, UserRole
from etablissements.models import Etablissement


class EtudiantForm(forms.ModelForm):
    """Formulaire pour créer un étudiant"""
    
    # Champs pour créer l'utilisateur
    email = forms.EmailField(
        required=True,
        label='Email',
        help_text='L\'email servira d\'identifiant de connexion',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'etudiant@example.com'
        })
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Mot de passe',
        help_text='Si non fourni, un mot de passe aléatoire sera généré',
        validators=[validate_password]
    )
    
    class Meta:
        model = Etudiant
        fields = ('nom', 'prenom', 'matricule', 'telephone')
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'matricule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: ETU2024001'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243900000000'
            }),
        }
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'matricule': 'Matricule',
            'telephone': 'Téléphone',
        }
    
    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec l'établissement"""
        etablissement = kwargs.pop('etablissement', None)
        super().__init__(*args, **kwargs)
        self.etablissement = etablissement
        
        # Si on modifie un étudiant existant, rendre l'email et le mot de passe optionnels
        if self.instance and self.instance.pk:
            self.fields['email'].required = False
            self.fields['email'].help_text = 'Laissez vide pour ne pas modifier l\'email'
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Laissez vide pour ne pas modifier le mot de passe'
    
    def clean_matricule(self):
        """Valide l'unicité du matricule"""
        matricule = self.cleaned_data.get('matricule')
        if matricule:
            matricule = matricule.strip().upper()
            # Vérifier l'unicité si l'établissement est défini
            if self.etablissement:
                existing = Etudiant.objects.filter(matricule=matricule, etablissement=self.etablissement)
                # Si on modifie, exclure l'instance actuelle
                if self.instance and self.instance.pk:
                    existing = existing.exclude(id=self.instance.id)
                if existing.exists():
                    raise forms.ValidationError(f"Un étudiant avec le matricule {matricule} existe déjà dans cet établissement.")
        return matricule
    
    def clean_email(self):
        """Valide l'unicité de l'email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Si on modifie, exclure l'utilisateur actuel
            existing = User.objects.filter(email=email)
            if self.instance and self.instance.pk and self.instance.user:
                existing = existing.exclude(id=self.instance.user.id)
            if existing.exists():
                raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        elif not email and (not self.instance or not self.instance.pk):
            # Email requis uniquement pour la création
            raise forms.ValidationError("L'email est requis pour créer un nouvel étudiant.")
        return email
    
    def clean_telephone(self):
        """Valide le format du téléphone"""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            telephone = telephone.strip().replace(' ', '').replace('-', '')
            if telephone.startswith('0'):
                telephone = '+243' + telephone[1:]
            elif telephone.startswith('243'):
                telephone = '+' + telephone
            elif not telephone.startswith('+'):
                if telephone.isdigit():
                    telephone = '+243' + telephone.lstrip('0')
        return telephone
    
    def save(self, commit=True):
        """Sauvegarde l'étudiant et crée/modifie l'utilisateur"""
        etudiant = super().save(commit=False)
        
        if not self.etablissement:
            raise ValueError("L'établissement doit être défini")
        
        etudiant.etablissement = self.etablissement
        
        if commit:
            # Si on modifie un étudiant existant
            if self.instance and self.instance.pk:
                # Mettre à jour l'utilisateur si email fourni
                email = self.cleaned_data.get('email')
                password = self.cleaned_data.get('password')
                
                if etudiant.user:
                    # Mettre à jour l'email si fourni
                    if email:
                        etudiant.user.email = email
                    # Mettre à jour le mot de passe si fourni
                    if password:
                        etudiant.user.set_password(password)
                    etudiant.user.save()
                elif email:
                    # Créer un utilisateur si email fourni mais pas d'utilisateur
                    if not password:
                        password = User.objects.make_random_password()
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        role=UserRole.ETUDIANT
                    )
                    etudiant.user = user
                    if not self.cleaned_data.get('password'):
                        self.generated_password = password
            else:
                # Créer un nouvel utilisateur
                email = self.cleaned_data.get('email')
                if not email:
                    raise ValueError("L'email est requis pour créer un nouvel étudiant")
                
                password = self.cleaned_data.get('password')
                if not password:
                    password = User.objects.make_random_password()
                
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role=UserRole.ETUDIANT
                )
                
                etudiant.user = user
                if not self.cleaned_data.get('password'):
                    self.generated_password = password
            
            etudiant.save()
        
        return etudiant

