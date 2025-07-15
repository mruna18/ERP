from rest_framework import serializers
from .models import *

class StaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
