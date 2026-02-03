"""
Serializers pour l'app etablissements
"""
from rest_framework import serializers
from .models import Etablissement, ComptePaiement
from core.serializers import UserSerializer


class ComptePaiementSerializer(serializers.ModelSerializer):
    """Serializer pour ComptePaiement"""
    
    class Meta:
        model = ComptePaiement
        fields = ('id', 'intitule', 'operateur', 'numero_compte', 'actif', 'date_creation')
        read_only_fields = ('id', 'date_creation')


class EtablissementSerializer(serializers.ModelSerializer):
    """Serializer pour Etablissement"""
    comptes_paiement = ComptePaiementSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)
    
    class Meta:
        model = Etablissement
        fields = (
            'id', 'nom', 'type', 'email', 'telephone', 'adresse',
            'logo', 'statut', 'date_inscription', 'admin', 'comptes_paiement'
        )
        read_only_fields = ('id', 'date_inscription')


class EtablissementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un établissement"""
    
    class Meta:
        model = Etablissement
        fields = ('nom', 'type', 'email', 'telephone', 'adresse', 'logo')


class ComptePaiementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un compte de paiement"""
    
    class Meta:
        model = ComptePaiement
        fields = ('etablissement', 'intitule', 'operateur', 'numero_compte', 'actif')

