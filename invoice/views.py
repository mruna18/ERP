from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from rest_framework.generics import RetrieveAPIView, ListAPIView

from .models import Invoice, InvoiceItem
from items.models import Item
from customer.models import Customer
from parties.models import Party
from .serializers import InvoiceSerializer


class CreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        party = data.get("party")
        items_data = request.data.get("items", [])  # Using raw request data for nested writable field

        # Validate Party ownership
        if party.company != customer.selected_company:
            return Response({"detail": "Party not found for selected company."}, status=status.HTTP_404_NOT_FOUND)

        subtotal = 0
        tax_total = 0

        with transaction.atomic():
            invoice = Invoice.objects.create(
                company=customer.selected_company,
                party=party,
                created_by=request.user,
                invoice_number=data["invoice_number"],
                notes=data.get("notes", ""),
            )

            for item_data in items_data:
                try:
                    item_obj = Item.objects.get(id=item_data["item"], company=customer.selected_company)
                except Item.DoesNotExist:
                    return Response({"detail": f"Item {item_data['item']} not found for selected company."}, status=status.HTTP_404_NOT_FOUND)

                quantity = item_data["quantity"]
                rate = item_data["rate"]
                amount = quantity * rate
                tax = amount * (item_obj.tax_percent / 100) if item_obj.tax_applied else 0

                subtotal += amount
                tax_total += tax

                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=item_obj,
                    quantity=quantity,
                    rate=rate,
                    amount=amount + tax
                )

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_total
            invoice.total = subtotal + tax_total
            invoice.save()

        return Response({
            "msg": "Invoice created",
            "invoice_id": invoice.id,
            "total_amount": invoice.total
        }, status=status.HTTP_201_CREATED)


class InvoiceDetailView(RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]


class InvoiceListView(ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = Customer.objects.filter(user=self.request.user).first()
        if not customer or not customer.selected_company:
            return Invoice.objects.none()
        return Invoice.objects.filter(company=customer.selected_company)


class UpdateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(pk=pk, company=customer.selected_company)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(invoice, data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        party = validated_data.get("party")
        if party.company != customer.selected_company:
            return Response({"detail": "Invalid party for selected company."},
                            status=status.HTTP_400_BAD_REQUEST)

        items_data = request.data.get("items", [])
        if not items_data:
            return Response({"detail": "At least one item is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        subtotal = 0
        tax_total = 0

        with transaction.atomic():
            invoice.party = party
            invoice.invoice_number = validated_data.get("invoice_number")
            invoice.notes = validated_data.get("notes", "")
            invoice.items.all().delete()  # Delete previous items

            for item_data in items_data:
                item_id = item_data.get("item")
                quantity = item_data.get("quantity")
                rate = item_data.get("rate")

                if not all([item_id, quantity, rate]):
                    return Response({"detail": "Each item must include item, quantity, and rate."},
                                    status=status.HTTP_400_BAD_REQUEST)

                try:
                    item_obj = Item.objects.get(id=item_id, company=customer.selected_company)
                except Item.DoesNotExist:
                    return Response({"detail": f"Item with id {item_id} not found for this company."},
                                    status=status.HTTP_400_BAD_REQUEST)

                amount = quantity * rate
                tax = amount * (item_obj.tax_percent / 100) if item_obj.tax_applied else 0

                subtotal += amount
                tax_total += tax

                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=item_obj,
                    quantity=quantity,
                    rate=rate,
                    amount=amount + tax
                )

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_total
            invoice.total = subtotal + tax_total
            invoice.save()

        return Response({
            "msg": "Invoice updated successfully",
            "invoice_id": invoice.id,
            "total": invoice.total
        }, status=status.HTTP_200_OK)


class DeleteInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(pk=pk, company=customer.selected_company)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        invoice.delete()
        return Response({"msg": "Invoice deleted successfully"}, status=status.HTTP_200_OK)