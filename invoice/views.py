from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from rest_framework.generics import RetrieveAPIView, ListAPIView

from .models import *
from items.models import Item
from customer.models import Customer
from parties.models import *
from .serializers import *
from django.db.models import Max
from .utils import *


# def generate_invoice_number(company):
#     last_invoice = Invoice.objects.filter(company=company).aggregate(Max('id'))['id__max']
#     next_id = (last_invoice or 0) + 1
#     return f"INV-{company.id:03d}-{next_id:05d}"


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
        warnings = []

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
                warnings.append(
                    f"Item '{item_obj.name}' has only {item_obj.quantity} in stock, but {quantity} were requested."
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

        invoice_discount_amount = subtotal * (invoice_discount_percent / 100)
        tax_total = 0.0
        invoice_total = 0.0

        with transaction.atomic():
            invoice_number = generate_invoice_number(company)

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

                item_invoice_discount_share = (taxable_amount / subtotal) * invoice_discount_amount if subtotal > 0 else 0.0
                final_taxable_amount = taxable_amount - item_invoice_discount_share
                tax = final_taxable_amount * (item_obj.tax_percent / 100) if item_obj.tax_applied else 0.0
                amount = final_taxable_amount + tax

                tax_total += tax
                invoice_total += amount

                if is_purchase:
                    item_obj.quantity += quantity
                elif is_sales:
                    item_obj.quantity = max(item_obj.quantity - quantity, 0)
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
            "invoice_number": invoice.invoice_number,
            "total_amount": invoice.total,
            "warnings": warnings,
            "status": 200
        })



# list of invoice related to the company
class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"detail": "Company ID is required.", "status":500})

        invoices = (
            Invoice.objects
            .filter(company_id=company_id)
            .select_related("company", "party", "invoice_type", "created_by")
            .order_by("-id")
        )

        response_data = []
        for invoice in invoices:
            response_data.append({
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "company_id": invoice.company.id,
                "company_name": invoice.company.name,
                "party_id": invoice.party.id,
                "party_name": invoice.party.name,
                "invoice_type": invoice.invoice_type.name,
                "subtotal": invoice.subtotal,
                "tax_amount": invoice.tax_amount,
                "total": invoice.total,
                "discount_percent": invoice.discount_percent,
                "discount_amount": invoice.discount_amount,
                "notes": invoice.notes,
                "created_by": invoice.created_by.username,
                "created_at": invoice.created_at,
            })

        return Response(response_data)


# class InvoiceListView(ListAPIView):
#     serializer_class = InvoiceSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         customer = Customer.objects.filter(user=self.request.user).first()
#         if not customer or not customer.selected_company:
#             return Invoice.objects.none()
#         return Invoice.objects.filter(company=customer.selected_company)

class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        items = []
        for item in invoice.items.all():
            items.append({
                "item_id": item.item.id,
                "item_name": item.item.name,
                "quantity": item.quantity,
                "rate": item.rate,
                "discount_percent": item.discount_percent,
                "discount_amount": item.discount_amount,
                "amount": item.amount
            })

        response_data = {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "company_id": invoice.company.id,
            "company_name": invoice.company.name,
            "party_id": invoice.party.id,
            "party_name": invoice.party.name,
            "invoice_type_id": invoice.invoice_type.id,
            "invoice_type_name": invoice.invoice_type.name,
            "discount_percent": invoice.discount_percent,
            "discount_amount": invoice.discount_amount,
            "tax_amount": invoice.tax_amount,
            "subtotal": invoice.subtotal,
            "total": invoice.total,
            "notes": invoice.notes,
            "created_at": invoice.created_at,
          
            "items": items
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class UpdateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"detail": "Company ID is required.", "status":500})

        try:
            invoice = Invoice.objects.get(pk=pk, company_id=company_id)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found for this company.", "status":500})

        serializer = InvoiceSerializer(invoice, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        party = data.get("party")
        if party.company_id != int(company_id):
            return Response({"detail": "Invalid party for the given company.", "status":500})

        invoice_type = data.get("invoice_type")
        if not invoice_type:
            return Response({"detail": "Invoice type is required.", "status":500})

        is_purchase = invoice_type.code.lower() == "purchase"
        is_sales = invoice_type.code.lower() == "sales"

        items_data = request.data.get("items", [])
        if not items_data:
            return Response({"detail": "At least one item is required.", "status":500})

        invoice_discount_percent = float(request.data.get("discount_percent", 0.0))
        subtotal = 0.0
        tax_total = 0.0
        item_rows = []
        warnings = []

        with transaction.atomic():
            invoice.items.all().delete()

            for item_data in items_data:
                try:
                    item_obj = Item.objects.get(id=item_data["item"], company_id=company_id)
                except Item.DoesNotExist:
                    return Response({"detail": f"Item {item_data['item']} not found for this company.", "status":500})

                quantity = item_data["quantity"]
                discount_percent = float(item_data.get("discount_percent", 0.0))

                if is_sales and item_obj.quantity < quantity:
                    warnings.append(
                        f"Item '{item_obj.name}' has only {item_obj.quantity} in stock, but {quantity} were requested."
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

            invoice_discount_amount = subtotal * (invoice_discount_percent / 100)
            invoice_total = 0.0

            for row in item_rows:
                item_obj = row["item"]
                quantity = row["quantity"]
                rate = row["rate"]
                discount_percent = row["discount_percent"]
                item_discount_amount = row["item_discount_amount"]
                taxable_amount = row["taxable_amount"]

                item_invoice_discount_share = (taxable_amount / subtotal) * invoice_discount_amount if subtotal > 0 else 0.0
                final_taxable = taxable_amount - item_invoice_discount_share
                tax = final_taxable * (item_obj.tax_percent / 100) if item_obj.tax_applied else 0.0
                amount = final_taxable + tax

                tax_total += tax
                invoice_total += amount

                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=item_obj,
                    quantity=quantity,
                    rate=rate,
                    discount_percent=discount_percent,
                    discount_amount=item_discount_amount,
                    amount=amount
                )

                # Update item stock based on invoice type
                if is_sales:
                    item_obj.quantity -= quantity
                elif is_purchase:
                    item_obj.quantity += quantity

                item_obj.save()

            invoice.party = party
            invoice.invoice_number = request.data.get("invoice_number") or invoice.invoice_number
            invoice.notes = data.get("notes", "")
            invoice.discount_percent = invoice_discount_percent
            invoice.discount_amount = invoice_discount_amount
            invoice.tax_amount = tax_total
            invoice.subtotal = subtotal
            invoice.total = invoice_total
            invoice.invoice_type = invoice_type
            invoice.save()

            # print("Invoice subtotal:", subtotal)
            # print("Invoice total:", invoice_total)
            # print("Invoice items:", InvoiceItem.objects.filter(invoice=invoice).count())

        return Response({
            "msg": "Invoice updated successfully",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "total_amount": invoice.total,
            "warnings": warnings,
            "status": 200
        })

class DeleteInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"detail": "Company ID is required.", "status":500})

        try:
            invoice = Invoice.objects.get(pk=pk, company_id=company_id, is_deleted=False)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found for this company.", "status":500})

        invoice.is_deleted = True
        invoice.save()

        return Response({"msg": "Invoice soft-deleted successfully.", "status":200})


