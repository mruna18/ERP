from rest_framework import serializers
from .models import Party

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name','address','gst_number','phone','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
