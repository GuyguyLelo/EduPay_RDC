"""
Views pour la gestion des établissements
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Etablissement, ComptePaiement
from .serializers import (
    EtablissementSerializer, EtablissementCreateSerializer,
    ComptePaiementSerializer, ComptePaiementCreateSerializer
)
from core.permissions import IsSuperAdmin, IsEtablissementAdmin


class EtablissementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des établissements"""
    queryset = Etablissement.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EtablissementCreateSerializer
        return EtablissementSerializer
    
    def get_queryset(self):
        """Filtre les établissements selon le rôle"""
        user = self.request.user
        
        if user.is_super_admin:
            return Etablissement.objects.all()
        elif user.is_etablissement_admin:
            # Retourner uniquement son établissement
            etablissement = user.etablissement_admin
            if etablissement:
                return Etablissement.objects.filter(id=etablissement.id)
        
        return Etablissement.objects.none()


class ComptePaiementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des comptes de paiement"""
    queryset = ComptePaiement.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ComptePaiementCreateSerializer
        return ComptePaiementSerializer
    
    def get_queryset(self):
        """Filtre les comptes selon l'établissement"""
        user = self.request.user
        
        if user.is_super_admin:
            return ComptePaiement.objects.all()
        elif user.is_etablissement_admin:
            etablissement = user.etablissement_admin
            if etablissement:
                return ComptePaiement.objects.filter(etablissement=etablissement)
        
        return ComptePaiement.objects.none()
