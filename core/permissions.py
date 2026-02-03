"""
Permissions personnalisées pour EduPay RDC
"""
from rest_framework import permissions
from .models import UserRole


class IsSuperAdmin(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est super administrateur"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsEtablissementAdmin(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est administrateur d'établissement"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ETABLISSEMENT_ADMIN
        )


class IsEtudiant(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est étudiant"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ETUDIANT
        )


class IsEtablissementAdminOrReadOnly(permissions.BasePermission):
    """Permission pour permettre la lecture à tous et l'écriture aux admins d'établissement"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ETABLISSEMENT_ADMIN
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission pour permettre la modification uniquement au propriétaire"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifier si l'utilisateur est le propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'etudiant') and hasattr(obj.etudiant, 'user'):
            return obj.etudiant.user == request.user
        
        return False

