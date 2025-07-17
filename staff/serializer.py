from rest_framework import serializers
from .models import *

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