"""
Views pour la gestion des étudiants
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Etudiant
from .serializers import EtudiantSerializer, EtudiantCreateSerializer
from core.permissions import IsEtablissementAdmin, IsEtudiant


class EtudiantViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des étudiants"""
    queryset = Etudiant.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EtudiantCreateSerializer
        return EtudiantSerializer
    
    def get_queryset(self):
        """Filtre les étudiants selon le rôle"""
        user = self.request.user
        
        if user.is_super_admin:
            return Etudiant.objects.all()
        elif user.is_etablissement_admin:
            etablissement = user.etablissement_admin
            if etablissement:
                return Etudiant.objects.filter(etablissement=etablissement)
        elif user.is_etudiant:
            if hasattr(user, 'etudiant'):
                return Etudiant.objects.filter(id=user.etudiant.id)
        
        return Etudiant.objects.none()
