"""
Serializers pour l'app frais
"""
from rest_framework import serializers
from .models import Frais
from etablissements.serializers import EtablissementSerializer


class FraisSerializer(serializers.ModelSerializer):
    """Serializer pour Frais"""
    etablissement = EtablissementSerializer(read_only=True)
    
    class Meta:
        model = Frais
        fields = (
            'id', 'etablissement', 'nom_frais', 'montant', 'devise',
            'annee_academique', 'description', 'actif', 'date_creation'
        )
        read_only_fields = ('id', 'date_creation')


class FraisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer des frais"""
    
    class Meta:
        model = Frais
        fields = ('etablissement', 'nom_frais', 'montant', 'devise', 'annee_academique', 'description', 'actif')

