from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Company
from invoice.models import *
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated


class CreatePaymentInView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        company_id = data.get('company')
        bank_id = data.get('bank_account')
        invoice_id = data.get('invoice')
        amount = float(data.get('amount', 0))

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"status": 404, "message": "Company not found"}, status=404)

        try:
            bank = BankAccount.objects.get(id=bank_id, company=company, deleted=False)
        except BankAccount.DoesNotExist:
            return Response({"status": 400, "message": "Invalid or inactive bank account for this company"}, status=400)

        invoice = Invoice.objects.filter(id=invoice_id, company=company).first()

        if not invoice:
            return Response({"status": 404, "message": "Invoice not found for this company"}, status=404)


        #? STRICT VALIDATION: prevent overpayment or duplicate payments
        if invoice.remaining_balance <= 0:
            return Response({
                "status": 400,
                "message": "Invoice is already fully paid. No further payment is required."
            }, status=400)

        if amount > invoice.remaining_balance:
            return Response({
                "status": 400,
                "message": f"Payment amount exceeds the remaining balance of ₹{invoice.remaining_balance:.2f}."
            }, status=400)
    
        # Step 1: Record the payment
        payment = PaymentIn.objects.create(
            company=company,
            invoice=invoice,
            amount=amount,
            bank_account=bank,
            note=data.get('note', '')
        )

        # Step 2: Update bank balance
        bank.current_balance += amount
        bank.save()

        # Step 3: Update invoice financials
        invoice.amount_paid += amount
        invoice.remaining_balance = max(invoice.total - invoice.amount_paid, 0)

        if invoice.amount_paid == 0:
            invoice.payment_status_id = 1  # Unpaid
        elif invoice.amount_paid < invoice.total:
            invoice.payment_status_id = 2  # Partially Paid
        else:
            invoice.payment_status_id = 3  # Paid

        invoice.save()

        return Response({
            "status": 201,
            "message": "Payment In recorded and invoice updated successfully",
            "data": PaymentInSerializer(payment).data
        }, status=201)


class CreatePaymentOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        company_id = data.get("company")
        invoice_id = data.get("invoice")
        amount = float(data.get("amount", 0))
        bank_account_id = data.get("bank_account")
        note = data.get("note", "")

        # Validate company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"status": 404, "message": "Company not found."}, status=404)

        # Validate invoice (optional)
        invoice = None
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id, company=company)
            except Invoice.DoesNotExist:
                return Response({"status": 404, "message": "Invoice not found for this company."}, status=404)

        # Validate bank account
        try:
            bank_account = BankAccount.objects.get(id=bank_account_id, company=company, deleted=False)
        except BankAccount.DoesNotExist:
            return Response({"status": 404, "message": "Bank account not found for this company."}, status=404)

        # Check balance
        if bank_account.current_balance < amount:
            return Response({"status": 400, "message": "Insufficient bank balance."}, status=400)

        # Create PaymentOut
        payment = PaymentOut.objects.create(
            company=company,
            invoice=invoice,
            amount=amount,
            bank_account=bank_account,
            note=note
        )

        # Update bank balance
        bank_account.current_balance -= amount
        bank_account.save()

        # Create BankTransaction
        BankTransaction.objects.create(
            bank_account=bank_account,
            transaction_type='debit',
            amount=amount,
            related_invoice=invoice,
            description=note or f"Payment Out (Invoice #{invoice.invoice_number})" if invoice else "Payment Out",
            balance_after_transaction=bank_account.current_balance
        )

        return Response({
            "status": 201,
            "message": "PaymentOut created successfully.",
            "data": {
                "id": payment.id,
                "amount": payment.amount,
                "invoice": invoice.id if invoice else None,
                "bank_account": bank_account.id,
                "note": note
            }
        }, status=201)      