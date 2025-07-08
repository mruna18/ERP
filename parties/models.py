from django.db import models
from companies.models import *
from django.conf import settings


# Create your models here.
class Party(models.Model):
    #fk
    PARTY_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES, default='customer')

    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='parties')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


