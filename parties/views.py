# views.py
from .models import Party
from .serializers import PartySerializer
from companies.models import Company  # Import this

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from parties.models import *  
from staff.permission import *

class PartyCreateView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
    

    def post(self, request):
        data = request.data.copy()

        #Validate company existence
        company_id = data.get("company")
        try:
            company = Company.objects.get(id=company_id)
            if not company.is_active:
                return Response({'error': 'Selected company is inactive.',"status":200})
        except Company.DoesNotExist:
            return Response({'error': 'Company with this ID does not exist.',"status":200})

        # Check for duplicate party name in same company
        party_name = data.get("name")
        if Party.objects.filter(name=party_name, company=company, deleted=False).exists():
            return Response({'error': 'Party with this name already exists in the selected company.',"status":200})

        # Manual serializer validation (to customize errors)
        serializer = PartySerializer(data=data)
        if not serializer.is_valid():
            # Customize error messages
            error_messages = []
            for field, messages in serializer.errors.items():
                error_messages.append(f"{field}: {messages[0]}")
            return Response({'error': ' | '.join(error_messages)})

    
        try:
            with transaction.atomic():
                party = Party.objects.create(
                    name=serializer.validated_data.get('name'),
                    email=serializer.validated_data.get('email'),
                    phone=serializer.validated_data.get('phone'),
                    gst_number=serializer.validated_data.get('gst_number'),
                    address=serializer.validated_data.get('address'),
                    party_type=serializer.validated_data.get('party_type'),
                    company=company,
                    created_by=request.user
                )
                response_serializer = PartySerializer(party)
                return Response({
                    'message': 'Party created successfully.',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e),"status":500})


# class PartyListView(APIView):
#     permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]

#     def get(self, request):
#         customer = Customer.objects.filter(user=request.user).first()
#         if not customer or not customer.selected_company:
#             return Response({"detail": "Customer or selected company not found."})

#         parties = Party.objects.filter(company=customer.selected_company, deleted=False)
#         serializer = PartySerializer(parties, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class PartyUpdateView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]


    def put(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in the request body."}, status=400)

        try:
            party = Party.objects.get(pk=pk, company_id=company_id, deleted=False)
        except Party.DoesNotExist:
            return Response({"error": "Party not found for this company."}, status=404)

        serializer = PartySerializer(party, data=request.data, partial=True)
        if not serializer.is_valid():
            error_messages = [f"{field}: {error[0]}" for field, error in serializer.errors.items()]
            return Response({"error": " | ".join(error_messages)}, status=400)

        with transaction.atomic():
            for field, value in serializer.validated_data.items():
                setattr(party, field, value)
            party.save()

        return Response({"message": "Party updated successfully."}, status=200)


class PartyDeleteView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]


    def delete(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in the request body."}, status=400)

        try:
            party = Party.objects.get(pk=pk, company_id=company_id, deleted=False)
        except Party.DoesNotExist:
            return Response({"error": "Party not found for this company."}, status=404)

        party.deleted = True
        party.save()
        return Response({"message": "Party deleted successfully (soft delete)."}, status=200)

class PartyDetailView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]


    def get(self, request, company_id, pk):
        try:
            party = Party.objects.get(pk=pk, company_id=company_id, deleted=False)
        except Party.DoesNotExist:
            return Response({"error": "Party not found for this company."}, status=404)

        serializer = PartySerializer(party)
        return Response({
            "message": "Party details fetched successfully.",
            "data": serializer.data
        }, status=200)



#?
class PartyListPostView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
 

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in request body."}, status=400)

        parties = Party.objects.filter(company_id=company_id, deleted=False)
        serializer = PartySerializer(parties, many=True)

        return Response({
            "message": "Party list fetched successfully.",
            "data": serializer.data
        }, status=200)
