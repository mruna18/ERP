from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'phone', 'gst_number', 'user', 'owner']
        read_only_fields = ['id', 'user', 'owner','created_at','updated_at']
