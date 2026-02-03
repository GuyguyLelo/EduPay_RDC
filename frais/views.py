"""
Views pour la gestion des frais
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Frais
from .serializers import FraisSerializer, FraisCreateSerializer
from core.permissions import IsEtablissementAdmin


class FraisViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des frais"""
    queryset = Frais.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FraisCreateSerializer
        return FraisSerializer
    
    def get_queryset(self):
        """Filtre les frais selon l'établissement"""
        user = self.request.user
        
        if user.is_super_admin:
            return Frais.objects.all()
        elif user.is_etablissement_admin:
            etablissement = user.etablissement_admin
            if etablissement:
                return Frais.objects.filter(etablissement=etablissement)
        
        # Les étudiants peuvent voir les frais de leur établissement
        elif user.is_etudiant:
            if hasattr(user, 'etudiant'):
                return Frais.objects.filter(
                    etablissement=user.etudiant.etablissement,
                    actif=True
                )
        
        return Frais.objects.none()
