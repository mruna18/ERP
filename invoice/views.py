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
from payments.models import *
from staff.permission import *


# def generate_invoice_number(company):
#     last_invoice = Invoice.objects.filter(company=company).aggregate(Max('id'))['id__max']
#     next_id = (last_invoice or 0) + 1
#     return f"INV-{company.id:03d}-{next_id:05d}"


class GETCompanyBankAccountView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Bank Transaction"
    required_permission = "view"

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({
                "status": 500,
                "message": "Missing 'company' in request body.",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        accounts = BankAccount.objects.filter(company_id=company_id, deleted=False)
        serializer = BankAccountSerializer(accounts, many=True)
        return Response({
            "status": 200,
            "message": "Bank accounts fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class POSTCompanyBankAccountView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Bank Transaction"
    required_permission = "create"

    def post(self, request):
        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "Bank account created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": 500,
            "message": "Invalid data. Bank account creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UpdateBankAccountView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Bank Transaction"
    required_permission = "update"

    def put(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({
                "status": 500,
                "message": "Missing 'company' in request body."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            bank_account = BankAccount.objects.get(pk=pk, company_id=company_id, deleted=False)
        except BankAccount.DoesNotExist:
            return Response({
                "status": 500,
                "message": "Bank account not found for this company or already deleted."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountSerializer(bank_account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "Bank account updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": 400,
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteBankAccountView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Bank Transaction"
    required_permission = "delete"

    def delete(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({
                "status": 400,
                "message": "Missing 'company' in request body."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            bank_account = BankAccount.objects.get(pk=pk, company_id=company_id, deleted=False)
        except BankAccount.DoesNotExist:
            return Response({
                "status": 500,
                "message": "Bank account not found for this company or already deleted."
            }, status=status.HTTP_404_NOT_FOUND)

        bank_account.deleted = True
        bank_account.save()

        return Response({
            "status": 200,
            "message": "Bank account soft-deleted successfully."
        }, status=status.HTTP_200_OK)

#!##################################INVOICE##############################################
class CreateInvoiceView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Invoice"
    required_permission = "create"


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

        amount_paid = float(request.data.get("amount_paid", 0.0))
        payment_mode_id = request.data.get("payment_mode")
        payment_type_id = request.data.get("payment_type")
        bank_account_id = request.data.get("bank_account")

        if party.company_id != company.id:
            return Response({"detail": "Party does not belong to the selected company.", "status": 400})

        try:
            invoice_type = InvoiceType.objects.get(id=invoice_type_id)
        except InvoiceType.DoesNotExist:
            return Response({"detail": "Invalid invoice type.", "status": 400})

        payment_mode = PaymentMode.objects.filter(id=payment_mode_id).first()
        payment_type = PaymentType.objects.filter(id=payment_type_id).first()
        bank_account = None

        # Validate bank account if provided
        if bank_account_id:
            try:
                bank_account = BankAccount.objects.get(id=bank_account_id, company=company, deleted=False)
            except BankAccount.DoesNotExist:
                return Response({
                    "detail": "Invalid or unauthorized bank account for this company.",
                    "status": 400
                })

        # Require bank account for non-cash payment if amount is paid
        if amount_paid > 0 and payment_type and payment_type.name.lower() != "cash in hand" and not bank_account:
            return Response({
                "detail": "Bank account is required for non-cash payments.",
                "status": 400
            })

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
                    "detail": f"Item {item_data['item']} not found in this company.",
                    "status": 400
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
                discount_amount=invoice_discount_amount,
                payment_mode=payment_mode,
                payment_type=payment_type,
                bank_account=bank_account,
                amount_paid=amount_paid
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
            invoice.remaining_balance = max(invoice_total - amount_paid, 0)

            if amount_paid == 0:
                invoice.payment_status_id = 1  # Unpaid
            elif amount_paid < invoice_total:
                invoice.payment_status_id = 2  # Partially Paid
            else:
                invoice.payment_status_id = 3  # Paid

            invoice.save()

            # Create bank transaction only for on_account and if bank provided
            if (
                amount_paid > 0 and
                payment_mode and payment_mode.code == 'on_account' and
                bank_account
            ):
                BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_type='debit',
                    amount=amount_paid,
                    related_invoice=invoice,
                    description=f"Payment for Invoice #{invoice.invoice_number}",
                    balance_after_transaction=bank_account.current_balance - amount_paid
                )
                bank_account.current_balance -= amount_paid
                bank_account.save()

        return Response({
            "msg": "Invoice created successfully",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "total_amount": invoice.total,
            "amount_paid": invoice.amount_paid,
            "remaining_balance": invoice.remaining_balance,
            "payment_status": invoice.payment_status.label if invoice.payment_status else None,
            "warnings": warnings,
            "status": 200
        })




# list of invoice related to the company
class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Invoice"
    required_permission = "view"
 


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
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Invoice"
    required_permission = "view"

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
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Invoice"
    required_permission = "update"
    

    def put(self, request, pk):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"detail": "Company ID is required.", "status": 500})

        try:
            invoice = Invoice.objects.get(pk=pk, company_id=company_id)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found for this company.", "status": 500})

        serializer = InvoiceSerializer(invoice, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        party = data.get("party")
        if party.company_id != int(company_id):
            return Response({"detail": "Invalid party for the given company.", "status": 500})

        invoice_type = data.get("invoice_type")
        if not invoice_type:
            return Response({"detail": "Invoice type is required.", "status": 500})

        is_purchase = invoice_type.code.lower() == "purchase"
        is_sales = invoice_type.code.lower() == "sales"

        items_data = request.data.get("items", [])
        if not items_data:
            return Response({"detail": "At least one item is required.", "status": 500})

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
                    return Response({"detail": f"Item {item_data['item']} not found for this company.", "status": 500})

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

            # update payment status
            invoice.remaining_balance = max(invoice.total - invoice.amount_paid, 0)

            if invoice.amount_paid == 0:
                invoice.payment_status_id = 1  # Unpaid
            elif invoice.amount_paid < invoice.total:
                invoice.payment_status_id = 2  # Partially Paid
            else:
                invoice.payment_status_id = 3  # Paid

            # Overpaid warning
            overpaid_amount = round(invoice.amount_paid - invoice.total, 2)
            invoice.overpaid_amount = overpaid_amount if overpaid_amount > 0 else 0

            invoice.save()

        response = {
            "msg": "Invoice updated successfully",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "total_amount": invoice.total,
            "warnings": warnings,
            "status": 200
        }

        if overpaid_amount > 0:
            response["overpaid_warning"] = f"This invoice has been overpaid by ₹{overpaid_amount:.2f}. Please review or issue a refund."

        return Response(response)

class DeleteInvoiceView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Invoice"
    required_permission = "delete"
 

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


