from rest_framework import serializers
from .models import Invoice, InvoiceItem
from companies.serializers import CompanySerializer
from parties.serializers import PartySerializer
from items.serializer import *


class InvoiceItemSerializer(serializers.ModelSerializer):
    item_details = ItemSerializer(source='item', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'item', 'item_details', 'quantity', 'rate', 'amount']
        read_only_fields = ['amount']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    company_details = CompanySerializer(source='company', read_only=True)
    party_details = PartySerializer(source='party', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'date',
            'company', 'company_details',
            'party', 'party_details',
            'subtotal', 'tax_amount', 'total',
            'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'company', 'company_details', 'date',
            'subtotal', 'tax_amount', 'total',
            'created_at', 'updated_at', 'items'
        ]

