from django.db import models
from companies.models import * 
from customer.models import * 
from invoice.models import * 
from django.utils import timezone

class BankTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.DO_NOTHING, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    related_invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    balance_after_transaction = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type.title()} ₹{self.amount} on {self.created_at.date()}"

class PaymentIn(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.DO_NOTHING)
    invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Payment In: ₹{self.amount} for {self.company.name}"


class PaymentOut(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.DO_NOTHING)
    invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Payment Out: ₹{self.amount} from {self.company.name}"


#! -- cash ledger --

class CashTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),  # Incoming cash
        ('debit', 'Debit'),    # Outgoing cash
    ]

    ledger = models.ForeignKey('CashLedger', on_delete=models.DO_NOTHING, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    balance_after_transaction = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.ledger.ledger_name} - {self.transaction_type} ₹{self.amount}"

class CashLedger(models.Model):
    ledger_name = models.CharField(max_length=50)
    company_name = models.ForeignKey(Company, on_delete=models.DO_NOTHING, null=True, blank=True)
    as_on = models.DateField(null=True, blank=True)
    opening_balance = models.FloatField(null=True, blank=True, default=0)
    current_balance = models.FloatField(null=True, blank=True, default=0)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.ledger_name
    

#! -- bank to bank 
class BankToBankTransfer(models.Model):
    company = models.ForeignKey(Company,on_delete=models.DO_NOTHING)
    from_account = models.ForeignKey(BankAccount,on_delete=models.DO_NOTHING, related_name='transfers_out')
    to_account = models.ForeignKey(BankAccount,on_delete=models.DO_NOTHING, related_name='transfers_in')
    amount = models.FloatField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False) 

    def __str__(self):
        return f"₹{self.amount} from {self.from_account} to {self.to_account}"

#!  excel - sales report
class ReportExportLog(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)  # e.g. "sales", "purchase"
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    filters_applied = models.JSONField(null=True, blank=True)
