from django.db import models


class BankTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    related_invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    balance_after_transaction = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type.title()} ₹{self.amount} on {self.created_at.date()}"

class PaymentIn(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Payment In: ₹{self.amount} for {self.company.name}"


class PaymentOut(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    invoice = models.ForeignKey('invoice.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    bank_account = models.ForeignKey('invoice.BankAccount', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Payment Out: ₹{self.amount} from {self.company.name}"
