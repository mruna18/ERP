from django.contrib.auth.models import User
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey("companies.Company", on_delete=models.DO_NOTHING)  
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
