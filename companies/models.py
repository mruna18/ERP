from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer
from django.db.models import Q
from django.utils import timezone

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, unique=True)
    gst_number = models.CharField(max_length=30, unique=True)
    # owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='companies', null=True)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='companies') 
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    is_active = models.BooleanField(default=True) 
    
    # class Meta:
    #     unique_together = ('name', 'gst_number')  # No duplicate company name per owner

    class Meta:
      constraints = [
        models.UniqueConstraint(fields=['gst_number'], condition=Q(is_active=True), name='unique_active_gst'),
        models.UniqueConstraint(fields=['phone'], condition=Q(is_active=True), name='unique_active_phone'),
    ]

    def __str__(self):
        return self.name
    



    
