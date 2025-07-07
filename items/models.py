from django.db import models
from companies.models import Company
from django.conf import settings
from decimal import Decimal

class Item(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilogram'),
        ('ltr', 'Litre'),
        ('box', 'Box'),
        ('unit', 'Unit'),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')

    price = models.FloatField()
    sales_price = models.FloatField()  # ✅ New field

    tax_applied = models.BooleanField(default=False)
    tax_percent = models.FloatField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="items")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_items"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
