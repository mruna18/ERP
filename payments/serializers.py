from rest_framework import serializers
from .models import *
from invoice.models import *

class BankAccountMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_name', 'account_no']

class InvoiceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'total', 'amount_paid', 'remaining_balance']

class PaymentInSerializer(serializers.ModelSerializer):
    bank_account = BankAccountMiniSerializer(read_only=True)
    invoice = InvoiceMiniSerializer(read_only=True)

    class Meta:
        model = PaymentIn
        fields = ['id', 'amount', 'payment_date', 'note', 'company', 'invoice', 'bank_account']

# class PaymentInSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentIn
#         fields = '__all__'


class PaymentOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOut
        fields = '__all__'

class CashLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashLedger
        fields = '__all__'

class CashTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = '__all__'