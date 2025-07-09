from rest_framework import serializers
from .models import Party

class PartySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    party_type_name = serializers.CharField(source='party_type.name', read_only=True)

    class Meta:
        model = Party
        fields = [
            'id', 'name', 'email', 'phone', 'gst_number', 'address',
            'party_type', 'party_type_name',
            'company', 'company_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name', 'party_type_name']
