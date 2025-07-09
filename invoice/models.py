from django.db import models
from django.conf import settings
from companies.models import Company
from items.models import Item
from parties.models import Party


class InvoiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Sales Invoice"
    code = models.CharField(max_length=20, unique=True)  # e.g., "sales", "purchase"

    def __str__(self):
        return self.name


class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    discount_percent = models.FloatField(default=0.0)
    discount_amount = models.FloatField(default=0.0)

    invoice_type = models.ForeignKey(InvoiceType, on_delete=models.PROTECT)

    notes = models.TextField(blank=True)
    subtotal = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number} ({self.invoice_type.code})"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    rate = models.FloatField() 
    amount = models.FloatField()
    discount_percent = models.FloatField(default=0.0)  # e.g. 10 for 10%
    discount_amount = models.FloatField(default=0.0) 

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
