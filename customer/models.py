from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    company_limit = models.PositiveIntegerField(default=3)  #default 3
    is_active = models.BooleanField(default=True) 
    

    def __str__(self):
        return self.user.username
