from django.db import models
from companies.models import Company
from django.conf import settings

# ------------------------------
# UnitType Model
# ------------------------------
class UnitType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Pieces", "Kilogram"
    code = models.CharField(max_length=10, unique=True)  # e.g., "pcs", "kg"

    def __str__(self):
        return f"{self.name} ({self.code})"

# ------------------------------
# Item Model
# ------------------------------
class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    quantity = models.PositiveIntegerField(default=0)
    unit = models.ForeignKey(UnitType, on_delete=models.PROTECT, related_name="items")

    price = models.FloatField()
    sales_price = models.FloatField()

    tax_applied = models.BooleanField(default=False)
    tax_percent = models.FloatField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="items")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_items"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
