from django.db import models
from django.conf import settings
from companies.models import Company
from items.models import Item
from parties.models import Party  


class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoices")
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="invoices")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices"
    )

    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)

    subtotal = models.FloatField(default=0.0)     # Before tax, after discounts
    tax_amount = models.FloatField(default=0.0)   # Total tax on invoice
    total = models.FloatField(default=0.0)        # Final total (subtotal + tax)

    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.company.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    quantity = models.FloatField(default=1)
    sales_price = models.FloatField()  
    discount = models.FloatField(default=0.0)  
    amount = models.FloatField()  

    def save(self, *args, **kwargs):
        raw_total = self.sales_price * self.quantity
        self.amount = raw_total - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} x {self.sales_price}"
