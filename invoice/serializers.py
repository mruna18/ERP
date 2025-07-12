from rest_framework import serializers
from .models import *
from companies.serializers import *
from parties.serializers import *
from items.serializer import *


# class InvoiceItemSerializer(serializers.ModelSerializer):
#     item_details = ItemSerializer(source='item', read_only=True)

#     class Meta:
#         model = InvoiceItem
#         fields = '__all__'
#         read_only_fields = ['amount']


# class InvoiceSerializer(serializers.ModelSerializer):
#     items = InvoiceItemSerializer(many=True, read_only=True)
#     company_details = CompanySerializer(source='company', read_only=True)
#     party_details = PartySerializer(source='party', read_only=True)

#     class Meta:
#         model = Invoice
#         fields = [
#             'id',
#             'invoice_number',
#             'date',
#             'company', 'company_details',
#             'party', 'party_details',
#             'subtotal', 'tax_amount', 'total',
#             'notes', 'items',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = [
#             'id', 'company', 'company_details', 'date',
#             'subtotal', 'tax_amount', 'total',
#             'created_at', 'updated_at', 'items'
#         ]

class InvoiceSerializer(serializers.ModelSerializer):
    
    party = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all())
    invoice_type = serializers.PrimaryKeyRelatedField(queryset=InvoiceType.objects.all())
    class Meta:
        model = Invoice
        fields = ['company', 'party', 'invoice_number', 'notes','invoice_type']  
        extra_kwargs = {
            "invoice_number": {"required": False}
        }



class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        # exclude = ['deleted']  # Hides the 'deleted' field
        fields ='__all__'


