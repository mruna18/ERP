from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            return Response({'message': 'User registered successfully', 'status':200})
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            # Authenticate 
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'username': user.username,
                    'email': user.email
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=404)


class CustomerCreateView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # 1. Create a user in auth_user
            user = User.objects.create_user(
                username=data['username'],
                password=data['password']
            )

            # 2. Create a customer linked to this user
            customer = Customer.objects.create(
                user=user,
                phone=data['phone'],
                address=data['address']
            )

            return Response({'msg': 'Customer created successfully'}, status=201)
        return Response(serializer.errors, status=400)
