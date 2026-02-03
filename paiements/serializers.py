"""
Serializers pour l'app paiements
"""
from rest_framework import serializers
from .models import Paiement, StatutPaiement
from etudiants.serializers import EtudiantSerializer
from frais.serializers import FraisSerializer


class PaiementSerializer(serializers.ModelSerializer):
    """Serializer pour Paiement"""
    etudiant = EtudiantSerializer(read_only=True)
    frais = FraisSerializer(read_only=True)
    montant_etablissement = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Paiement
        fields = (
            'id', 'etudiant', 'frais', 'montant', 'devise', 'statut',
            'reference_flutterwave', 'transaction_id', 'commission_plateforme',
            'taux_commission', 'montant_etablissement', 'date_paiement',
            'date_creation', 'numero_telephone', 'operateur', 'message_erreur'
        )
        read_only_fields = (
            'id', 'reference_flutterwave', 'transaction_id',
            'commission_plateforme', 'date_paiement', 'date_creation', 'message_erreur'
        )


class PaiementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un paiement"""
    numero_telephone = serializers.CharField(required=True)
    operateur = serializers.CharField(required=True)
    
    class Meta:
        model = Paiement
        fields = ('etudiant', 'frais', 'numero_telephone', 'operateur', 'taux_commission')
    
    def validate(self, attrs):
        # Le montant et la devise sont récupérés du frais
        frais = attrs['frais']
        if not frais.actif:
            raise serializers.ValidationError("Ce frais n'est plus actif.")
        return attrs
    
    def create(self, validated_data):
        frais = validated_data['frais']
        taux_commission = validated_data.pop('taux_commission', 2.0)
        
        paiement = Paiement.objects.create(
            montant=frais.montant,
            devise=frais.devise,
            taux_commission=taux_commission,
            **validated_data
        )
        
        return paiement


class WebhookSerializer(serializers.Serializer):
    """Serializer pour les webhooks CinetPay"""
    event = serializers.CharField()
    data = serializers.DictField()

