from django.utils.timezone import now
from .models import Invoice

def generate_invoice_number(company):
    year = now().year
    prefix = f"INV-{year}-"

    last_invoice = Invoice.objects.filter(company=company, invoice_number__startswith=prefix) \
        .order_by("invoice_number").last()

    if last_invoice and last_invoice.invoice_number:
        try:
            last_number = int(last_invoice.invoice_number.split("-")[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    next_number = str(last_number + 1).zfill(3)
    return f"{prefix}{next_number}"
