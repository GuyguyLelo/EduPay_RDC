"""
Serializers pour l'app etudiants
"""
from rest_framework import serializers
from .models import Etudiant
from etablissements.serializers import EtablissementSerializer
from core.serializers import UserSerializer


class EtudiantSerializer(serializers.ModelSerializer):
    """Serializer pour Etudiant"""
    user = UserSerializer(read_only=True)
    etablissement = EtablissementSerializer(read_only=True)
    nom_complet = serializers.CharField(source='nom_complet', read_only=True)
    
    class Meta:
        model = Etudiant
        fields = (
            'id', 'user', 'nom', 'prenom', 'matricule', 'etablissement',
            'telephone', 'date_inscription', 'nom_complet'
        )
        read_only_fields = ('id', 'date_inscription')


class EtudiantCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un étudiant"""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Etudiant
        fields = ('nom', 'prenom', 'matricule', 'etablissement', 'telephone', 'email', 'password')
    
    def create(self, validated_data):
        from core.models import User, UserRole
        
        email = validated_data.pop('email')
        password = validated_data.pop('password', None)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email,
            password=password or User.objects.make_random_password(),
            role=UserRole.ETUDIANT
        )
        
        # Créer l'étudiant
        etudiant = Etudiant.objects.create(user=user, **validated_data)
        return etudiant

