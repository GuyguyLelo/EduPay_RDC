"""
Custom User Model pour EduPay RDC
Gestion des utilisateurs avec rôles : SUPER_ADMIN, ETABLISSEMENT_ADMIN, ETUDIANT
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """Rôles disponibles dans le système"""
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Administrateur'
    ETABLISSEMENT_ADMIN = 'ETABLISSEMENT_ADMIN', 'Administrateur Établissement'
    ETUDIANT = 'ETUDIANT', 'Étudiant'


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur avec email et mot de passe"""
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un super utilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé
    Utilise email comme identifiant unique au lieu de username
    """
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ETUDIANT,
        verbose_name='Rôle'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    is_staff = models.BooleanField(default=False, verbose_name='Staff')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date d\'inscription')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Dernière connexion')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email.split('@')[0]
    
    @property
    def is_super_admin(self):
        """Vérifie si l'utilisateur est super administrateur"""
        return self.role == UserRole.SUPER_ADMIN
    
    @property
    def is_etablissement_admin(self):
        """Vérifie si l'utilisateur est administrateur d'établissement"""
        return self.role == UserRole.ETABLISSEMENT_ADMIN
    
    @property
    def is_etudiant(self):
        """Vérifie si l'utilisateur est étudiant"""
        return self.role == UserRole.ETUDIANT
