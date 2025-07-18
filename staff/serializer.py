from rest_framework import serializers
from .models import *
from companies.models import *

class StaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ModulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulePermission
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']


class StaffProfileSerializer(serializers.ModelSerializer):
    job_role_name = serializers.CharField(source='job_role.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = StaffProfile
        fields = ['id', 'username', 'email', 'job_role_name', 'company_name', 'is_active', 'created_at']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'gst_number']