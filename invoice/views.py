from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from rest_framework.generics import RetrieveAPIView, ListAPIView

from .models import *
from items.models import *
from customer.models import *
from parties.models import *
from .serializers import *
from companies.models import *


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from .models import Invoice, InvoiceItem, InvoiceType
from items.models import Item
from customer.models import Customer
from parties.models import Party
from .serializers import InvoiceSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from .models import Invoice, InvoiceItem, InvoiceType
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
        if not customer:
            return Response({"detail": "Customer not found.", "status": 500})

        data = serializer.validated_data
        company = data["company"]
        party = data["party"]
        invoice_number = data["invoice_number"]
        invoice_type_id = request.data.get("invoice_type")
        notes = data.get("notes", "")
        items_data = request.data.get("items", [])
        invoice_discount_percent = float(request.data.get("discount_percent", 0.0))

        if party.company_id != company.id:
            return Response({"detail": "Party does not belong to the provided company.", "status": 500})

        try:
            invoice_type = InvoiceType.objects.get(id=invoice_type_id)
        except InvoiceType.DoesNotExist:
            return Response({"detail": "Invalid invoice type.", "status": 500})

        is_purchase = invoice_type.code.lower() == "purchase"
        is_sales = invoice_type.code.lower() == "sales"

        item_rows = []
        subtotal = 0.0

        # Step 1: Pre-calculate all base values
        for item_data in items_data:
            try:
                item_obj = Item.objects.get(id=item_data["item"], company=company)
            except Item.DoesNotExist:
                return Response({
                    "detail": f"Item {item_data['item']} not found in the selected company.",
                    "status": 500
                })

            quantity = item_data["quantity"]
            discount_percent = float(item_data.get("discount_percent", 0.0))

            if is_sales and item_obj.quantity < quantity:
                return Response(
                    {"detail": f"Insufficient stock for item '{item_obj.name}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            rate = item_obj.sales_price
            base_amount = quantity * rate
            item_discount_amount = base_amount * (discount_percent / 100)
            taxable_amount = base_amount - item_discount_amount

            subtotal += taxable_amount

            item_rows.append({
                "item": item_obj,
                "quantity": quantity,
                "rate": rate,
                "discount_percent": discount_percent,
                "item_discount_amount": item_discount_amount,
                "taxable_amount": taxable_amount
            })

        # Step 2: Start DB transaction
        tax_total = 0.0
        invoice_discount_amount = subtotal * (invoice_discount_percent / 100)
        subtotal_after_discount = subtotal - invoice_discount_amount
        invoice_total = 0.0

        with transaction.atomic():
            invoice = Invoice.objects.create(
                company=company,
                party=party,
                created_by=request.user,
                invoice_number=invoice_number,
                invoice_type=invoice_type,
                notes=notes,
                discount_percent=invoice_discount_percent,
                discount_amount=invoice_discount_amount
            )

            for row in item_rows:
                item_obj = row["item"]
                quantity = row["quantity"]
                rate = row["rate"]
                discount_percent = row["discount_percent"]
                item_discount_amount = row["item_discount_amount"]
                taxable_amount = row["taxable_amount"]

                # Apply proportional invoice-level discount
                if subtotal > 0:
                    item_invoice_discount_share = (taxable_amount / subtotal) * invoice_discount_amount
                else:
                    item_invoice_discount_share = 0.0

                final_taxable_amount = taxable_amount - item_invoice_discount_share
                tax = final_taxable_amount * (item_obj.tax_percent / 100) if item_obj.tax_applied else 0.0
                amount = final_taxable_amount + tax

                tax_total += tax
                invoice_total += amount

                if is_purchase:
                    item_obj.quantity += quantity
                elif is_sales:
                    item_obj.quantity -= quantity
                item_obj.save()

                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=item_obj,
                    quantity=quantity,
                    rate=rate,
                    discount_percent=discount_percent,
                    discount_amount=item_discount_amount,
                    amount=amount
                )

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_total
            invoice.total = invoice_total
            invoice.save()

        return Response({
            "msg": "Invoice created successfully",
            "invoice_id": invoice.id,
            "total_amount": invoice.total,
            "status": 200
        })

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
            return Response({"detail": "Customer or selected company not found." , "status":500})

        try:
            invoice = Invoice.objects.get(pk=pk, company=customer.selected_company)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found.","status":500})

        invoice.delete()
        return Response({"msg": "Invoice deleted successfully"}, status=status.HTTP_200_OK)