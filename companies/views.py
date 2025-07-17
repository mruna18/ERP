from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from companies.models import *
from customer.models import *
from companies.serializers import *
import re
from staff.models import *
from staff.management.commands.seed_permissions import *
from staff.permission import *
from staff.constant import *
from staff.models import *


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return Customer.objects.filter(user=request.user).exists()
class CreateCompanyView(APIView):
    permission_classes =[IsAuthenticated,IsCustomer]

    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=404)

        if customer.companies.count() >= customer.company_limit:
            return Response({"error": "Company creation limit reached"}, status=403)

        company_name = request.data.get('name')
        gst_number = request.data.get('gst_number')
        phone = request.data.get('phone')

        if not company_name:
            return Response({"error": "Company name is required."}, status=400)
        if not gst_number:
            return Response({"error": "GST number is required."}, status=400)
        if not phone:
            return Response({"error": "Phone number is required."}, status=400)
        if not re.fullmatch(r"\d{10}", phone):
            return Response({"error": "Phone number must be exactly 10 digits."}, status=400)

        if Company.objects.filter(phone=phone, owner=customer, is_active=True).exists():
            return Response({"error": "Company with this phone already exists."}, status=400)
        if Company.objects.filter(gst_number=gst_number, owner=customer, is_active=True).exists():
            return Response({"error": "Company with this GST number already exists."}, status=400)
        if Company.objects.filter(name=company_name, gst_number=gst_number, owner=customer, is_active=True).exists():
            return Response({"error": "Company with same name and GST already exists for this user"}, status=400)

        # Create the company
        company = Company.objects.create(
            name=company_name,
            gst_number=gst_number,
            phone=phone,
            address=request.data.get('address', ''),
            user=request.user,
            owner=customer,
        )

        # Assign default roles and permissions
        # from staff.constant import DEFAULT_ROLES
        # for role_name, permission_codes in DEFAULT_ROLES.items():
        #     role, created = Role.objects.get_or_create(name=role_name, company=company)
        #     for code in permission_codes:
        #         permission = CustomPermission.objects.filter(code=code).first()
        #         if permission:
        #             role.permissions.add(permission)

        # Assign Admin role to the creator
        admin_role = Role.objects.filter(company=company, name="Admin").first()
        if admin_role:
            StaffProfile.objects.create(
                company=company,
                user=request.user,
                role=admin_role,
                is_active=True
            )

        return Response({
            "msg": "Company created successfully",
            "company_id": company.id,
            "name": company.name
        }, status=201)


# Helper function to get logged-in customer
def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return None
    


class CompanyListView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]
   
    
    def get(self, request):
        customer = get_customer(request.user)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)

        companies = Company.objects.filter(owner=customer, is_active=True)
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned]
   

    def get(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer)
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)


class CompanyUpdateView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
  

    def put(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)

        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Company updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=400)


class CompanyDeleteView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
   
    def delete(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)

        company.is_active = False
        company.save()
        return Response({'msg': 'Company soft deleted successfully'}, status=204)



#! select the compnay
class SelectCompanyView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]

    def post(self, request):
        company_id = request.data.get('company_id')
        customer = get_customer(request.user)
        if not customer:
            return Response({"error": "Customer not found"}, status=404)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"error": "Company not found or inactive"}, status=404)

        customer.selected_company = company
        customer.save()
        return Response({"msg": f"{company.name} set as selected company."})
