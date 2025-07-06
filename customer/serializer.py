from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Customer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'address']


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # User-related display fields
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username_display = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'password',
            'phone',
            'address',
            'company_limit',
            'user_id',
            'username_display',
            'email',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']
