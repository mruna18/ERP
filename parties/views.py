from .models import Party, PartyType
from .serializers import PartySerializer
from companies.models import Company
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from parties.models import *
from staff.models import *
from staff.permission import *


class PartyTypeListView(APIView):
    """List party types (Customer, Supplier) for create form dropdown."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Auto-create default party types if they don't exist
        PartyType.objects.get_or_create(name='Customer')
        PartyType.objects.get_or_create(name='Supplier')
        
        party_types = PartyType.objects.all().order_by('id')
        data = [{"id": pt.id, "name": pt.name} for pt in party_types]
        return Response(data, status=status.HTTP_200_OK)



class PartyCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Party"
    required_permission = "create"

    def post(self, request):
        data = request.data.copy()
        company_id = data.get("company")

        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        # Check for duplicate party name
        party_name = data.get("name")
        if Party.objects.filter(name=party_name, company=company, deleted=False).exists():
            return Response({'error': 'Party with this name already exists in the selected company.', "status": 200})

        serializer = PartySerializer(data=data)
        if not serializer.is_valid():
            error_messages = [f"{field}: {messages[0]}" for field, messages in serializer.errors.items()]
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
            return Response({'error': str(e), "status": 500})


class PartyUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Party"
    required_permission = "edit"

    def put(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in the request body."}, status=400)

        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            party = Party.objects.get(pk=pk, company=company, deleted=False)
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
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Party"
    required_permission = "delete"

    def delete(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in the request body."}, status=400)

        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            party = Party.objects.get(pk=pk, company=company, deleted=False)
        except Party.DoesNotExist:
            return Response({"error": "Party not found for this company."}, status=404)

        party.deleted = True
        party.save()
        return Response({"message": "Party deleted successfully (soft delete)."}, status=200)


class PartyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Party"
    required_permission = "view_specific"

    def get(self, request, company_id, pk):
        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            party = Party.objects.get(pk=pk, company=company, deleted=False)
        except Party.DoesNotExist:
            return Response({"error": "Party not found for this company."}, status=404)

        serializer = PartySerializer(party)
        return Response({
            "message": "Party details fetched successfully.",
            "data": serializer.data
        }, status=200)


class PartyListPostView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Party"
    required_permission = "get_using_post"

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required in request body."}, status=400)

        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        parties = Party.objects.filter(company=company, deleted=False)
        serializer = PartySerializer(parties, many=True)
        return Response({
            "message": "Party list fetched successfully.",
            "data": serializer.data
        }, status=200)
