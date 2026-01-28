from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from django.contrib.auth import authenticate
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from staff.permission import *
from companies.serializers import *


class RegisterView(APIView):
    

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # 1. Create User
            user = User.objects.create_user(
                username=data['username'],
                email=data.get('email'),
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )

            # 2. Create related Customer entry
            Customer.objects.create(
                user=user,
                phone=data.get('phone', ''),
                address=data.get('address', '')
            )

            return Response({'message': 'User and Customer registered successfully', 'status': 200})
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'username': user.username,
                    'email': user.email
                }, status=200)
            else:
                return Response({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=404)
        


# class CustomerCreateView(APIView):
#     def post(self, request):
#         serializer = CustomerSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.validated_data

#             # Create User
#             user = User.objects.create_user(
#                 username=data['username'],
#                 password=data['password']
#             )

#             # Create Customer
#             Customer.objects.create(
#                 user=user,
#                 phone=data['phone'],
#                 address=data['address']
#             )

#             return Response({'msg': 'Customer created successfully'}, status=201)
#         return Response(serializer.errors, status=400)


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({
                "access_token": str(access_token)
            }, status=200)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=401)
        


#! superadmin
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
    

# ----------- Get Current Customer (Me) -----------
class CurrentCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user, is_active=True)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer profile not found'}, status=404)


# ----------- List All Customers -----------
class CustomerListView(APIView):
    permission_classes =[IsAuthenticated, IsSuperAdmin]
   

    def get(self, request):
        customers = Customer.objects.filter(is_active=True)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


# ----------- Retrieve Single Customer -----------
class CustomerRetrieveView(APIView):
    permission_classes =[IsAuthenticated, IsSuperAdminOrSelf]
  
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)
        
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


# ----------- Update Customer -----------
class CustomerUpdateView(APIView):
    permission_classes =[IsAuthenticated,IsSuperAdminOrSelf]

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            data = serializer.validated_data

            # Update Customer fields
            customer.phone = data.get('phone', customer.phone)
            customer.address = data.get('address', customer.address)
            customer.company_limit = data.get('company_limit', customer.company_limit)
            customer.save()

            # Update related User fields
            user = customer.user
            user.username = data.get('username', user.username)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.save()

            return Response({'msg': 'Customer updated successfully'})
        return Response(serializer.errors, status=400)



# ----------- Delete Customer -----------
class CustomerDeleteView(APIView):
    permission_classes =[IsAuthenticated, IsSuperAdmin]
   

    def delete(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        customer.is_active = False  
        customer.save()

        return Response({'msg': 'Customer soft deleted successfully'}, status=200)


