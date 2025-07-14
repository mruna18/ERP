from django.db import models
from django.conf import settings
from companies.models import Company
from items.models import Item
from parties.models import Party


class PaymentType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., 'Cash', 'Bank Transfer', 'Cheque'

    def __str__(self):
        return self.name
    
class PaymentMode(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "On Account", "Advance"
    code = models.CharField(max_length=30, unique=True)  # e.g., "on_account", "advance"

    def __str__(self):
        return self.name
    
class PaymentStatus(models.Model):
    # STATUS_CHOICES = (
    #     (1, 'Unpaid'),
    #     (2, 'Partially Paid'),
    #     (3, 'Paid'),
    # )

    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.label


class InvoiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Sales Invoice"
    code = models.CharField(max_length=20, unique=True)  # e.g., "sales", "purchase"

    def __str__(self):
        return self.name


class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoices')
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    invoice_number = models.CharField(max_length=50)
    invoice_type = models.ForeignKey('InvoiceType', on_delete=models.PROTECT)

    discount_percent = models.FloatField(default=0.0)
    discount_amount = models.FloatField(default=0.0)
    
    subtotal = models.FloatField(default=0.0)
    tax_amount = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)

    amount_paid = models.FloatField(default=0.0)
    remaining_balance = models.FloatField(default=0.0)

    payment_mode = models.ForeignKey('PaymentMode', on_delete=models.SET_NULL, null=True, blank=True)
    # payment_modes = models.ManyToManyField('PaymentMode', blank=True)
    payment_type = models.ForeignKey('PaymentType', on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.ForeignKey('PaymentStatus', on_delete=models.SET_NULL, null=True, blank=True)
    bank_account = models.ForeignKey('BankAccount', on_delete=models.SET_NULL, null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

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
# Optionally add:
    # is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class BankAccount(models.Model):
    account_no = models.CharField(max_length=18, null=True, blank=True)
    user = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    bank_name = models.CharField(max_length=50)
    bank_branch = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, null=True, blank=True)
    as_on = models.DateField(null=True, blank=True)
    opening_balance = models.FloatField(default=0.0, null=True, blank=True)
    current_balance = models.FloatField(default=0.0, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    swift_code = models.CharField(max_length=100, null=True, blank=True)
    ad_code = models.CharField(max_length=250, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bank_name} ({self.account_no})"



# class BankTransaction(models.Model):
#     TRANSACTION_TYPE_CHOICES = (
#         ('credit', 'Credit'),  # money added to the bank
#         ('debit', 'Debit'),    # money taken from the bank
#     )

#     bank_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name='transactions')
#     transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
#     amount = models.FloatField()
#     date = models.DateField(auto_now_add=True)
#     related_invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True)  # Optional
#     description = models.TextField(blank=True, null=True)

#     balance_after_transaction = models.FloatField(null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     # Optional logic to auto-compute `balance_after_transaction`
    #     if not self.pk:
    #         last_balance = self.bank_account.current_balance or 0.0
    #         if self.transaction_type == 'credit':
    #             new_balance = last_balance + self.amount
    #         else:
    #             new_balance = last_balance - self.amount

    #         self.balance_after_transaction = new_balance
    #         self.bank_account.current_balance = new_balance
    #         self.bank_account.save()

    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.transaction_type.title()} ₹{self.amount} on {self.date}"


