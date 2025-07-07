# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Party
from .serializers import PartySerializer
from customer.models import Customer

class PartyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PartySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(company=customer.selected_company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class PartyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        parties = Party.objects.filter(company=customer.selected_company, is_active=True)
        serializer = PartySerializer(parties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PartyUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            party = Party.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Party.DoesNotExist:
            return Response({"detail": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PartySerializer(party, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for field, value in serializer.validated_data.items():
                setattr(party, field, value)
            party.save()

        return Response({"msg": "Party updated"}, status=status.HTTP_200_OK)


class PartyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            party = Party.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Party.DoesNotExist:
            return Response({"detail": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

        party.is_active = False
        party.save()
        return Response({"msg": "Party deleted (soft)"}, status=status.HTTP_200_OK)


class PartyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            party = Party.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Party.DoesNotExist:
            return Response({"detail": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PartySerializer(party)
        return Response(serializer.data, status=status.HTTP_200_OK)