from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import *
from .serializers import *
from customer.models import Customer

class CreateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=404)

        # Enforce company creation limit
        if customer.companies.count() >= customer.company_limit:
            return Response({"error": "Company creation limit reached"}, status=403)

        # Check duplicate company
        if Company.objects.filter(name=request.data.get('name'), gst_number=request.data.get('gst_number'), owner=customer, is_active=True).exists():
            return Response({"error": "Company with same name and GST already exists for this user"}, status=400)

        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, owner=customer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Helper function to get logged-in customer
def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return None


class CompanyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = get_customer(request.user)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)

        companies = Company.objects.filter(owner=customer, is_active=True)
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer)
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)


class CompanyUpdateView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
