from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Company
from invoice.models import *
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import traceback


class CreatePaymentInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        company_id = data.get('company')
        invoice_id = data.get('invoice')
        bank_id = data.get('bank_account')  
        amount = float(data.get('amount', 0))

        # Validate company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"status": 404, "message": "Company not found"}, status=404)

        # Validate invoice
        try:
            invoice = Invoice.objects.get(id=invoice_id, company=company)
        except Invoice.DoesNotExist:
            return Response({"status": 404, "message": "Invoice not found for this company"}, status=404)

        #bank validation
        bank = None
        if bank_id:
            try:
                bank = BankAccount.objects.get(id=bank_id, company=company, deleted=False)
            except BankAccount.DoesNotExist:
                return Response({"status": 400, "message": "Invalid or inactive bank account for this company"}, status=400)

        # Prevent overpayment
        if invoice.remaining_balance <= 0:
            return Response({
                "status": 400,
                "message": "Invoice is already fully paid. No further payment is required."
            }, status=400)

        if round(amount, 2) > round(invoice.remaining_balance, 2):
            return Response({
                "status": 400,
                "message": f"Payment amount exceeds the remaining balance of ₹{invoice.remaining_balance:.2f}."
            }, status=400)

        #Create PaymentIn record
        payment = PaymentIn.objects.create(
            company=company,
            invoice=invoice,
            amount=amount,
            bank_account=bank,  # can be None
            note=data.get('note', '')
        )

        # Update bank balance and create bank transaction only if bank is used
        if bank:
            bank.current_balance += amount
            bank.save()

            BankTransaction.objects.create(
                bank_account=bank,
                transaction_type='credit',
                amount=amount,
                related_invoice=invoice,
                description=data.get('note', f"Payment In for invoice #{invoice.invoice_number}"),
                balance_after_transaction=bank.current_balance
            )

        # Update invoice
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
    

#! -- cash ledger --
class CreateCashLedgerView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        try:
            data = request.data

            company_id = data.get("company_name")
            ledger_name = data.get("ledger_name")
            opening_balance = float(data.get("opening_balance", 0))
            as_on = data.get("as_on")

            if not company_id or not ledger_name:
                return Response({"msg": "company_name and ledger_name are required", "status": 400})

            company = Company.objects.filter(id=company_id).first()
            if not company:
                return Response({"msg": "Company not found", "status": 404})

            if CashLedger.objects.filter(ledger_name=ledger_name, company_name=company, deleted=False).exists():
                return Response({"msg": "Cash Ledger already exists", "status": 400})

            ledger = CashLedger.objects.create(
                ledger_name=ledger_name,
                company_name=company,
                opening_balance=opening_balance,
                current_balance=opening_balance,
                as_on=as_on
            )

            return Response({
                "msg": "Cash Ledger Created Successfully",
                "data": {
                    "id": ledger.id,
                    "ledger_name": ledger.ledger_name,
                    "company_name": ledger.company_name.id,
                    "opening_balance": ledger.opening_balance,
                    "current_balance": ledger.current_balance,
                    "as_on": ledger.as_on
                },
                "status": 201
            })

        except Exception as e:
            import traceback
            return Response({"msg": traceback.format_exc(), "status": 500})
        

# cash transaction 
class CreateCashTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            ledger_id = data.get("ledger")
            transaction_type = data.get("transaction_type")
            amount = float(data.get("amount", 0))
            description = data.get("description", "")

            if not ledger_id or not transaction_type or amount <= 0:
                return Response({"status": 400, "message": "Invalid input data."}, status=400)

            try:
                ledger = CashLedger.objects.get(id=ledger_id, deleted=False)
            except CashLedger.DoesNotExist:
                return Response({"status": 404, "message": "Cash ledger not found."}, status=404)

            # Compute new balance
            if transaction_type == 'credit':
                new_balance = ledger.current_balance + amount
            elif transaction_type == 'debit':
                if amount > ledger.current_balance:
                    return Response({
                        "status": 400,
                        "message": "Insufficient cash balance for debit."
                    }, status=400)
                new_balance = ledger.current_balance - amount
            else:
                return Response({"status": 400, "message": "Invalid transaction type."}, status=400)

            with transaction.atomic():
                # Create transaction
                txn = CashTransaction.objects.create(
                    ledger=ledger,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    balance_after_transaction=new_balance
                )

                # Update ledger balance
                ledger.current_balance = new_balance
                ledger.save()

            return Response({
                "status": 201,
                "message": "Cash transaction created successfully.",
                "data": CashTransactionSerializer(txn).data
            }, status=201)

        except Exception:
            return Response({
                "status": 500,
                "message": traceback.format_exc()
            }, status=500)
        

class UpdateCashLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            ledger = CashLedger.objects.get(pk=pk, deleted=False)
        except CashLedger.DoesNotExist:
            return Response({"msg": "Cash ledger not found", "status": 404}, status=404)

        serializer = CashLedgerSerializer(ledger, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Cash ledger updated successfully", "data": serializer.data, "status": 200})
        else:
            return Response({"msg": serializer.errors, "status": 400}, status=400)
        


class DeleteCashLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            ledger = CashLedger.objects.get(pk=pk, deleted=False)
        except CashLedger.DoesNotExist:
            return Response({"msg": "Cash ledger not found", "status": 404}, status=404)

        ledger.deleted = True
        ledger.save()
        return Response({"msg": "Cash ledger soft-deleted successfully", "status": 200})


# list of all ledger
class ListCashLedgersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        ledgers = CashLedger.objects.filter(company_name_id=company_id, deleted=False)
        serializer = CashLedgerSerializer(ledgers, many=True)
        return Response({"msg": "Success", "data": serializer.data, "status": 200})
    
# get ledger by id
class GetCashLedgerByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            ledger = CashLedger.objects.get(pk=pk, deleted=False)
        except CashLedger.DoesNotExist:
            return Response({"msg": "Cash ledger not found", "status": 404}, status=404)

        serializer = CashLedgerSerializer(ledger)
        return Response({"msg": "Success", "data": serializer.data, "status": 200})