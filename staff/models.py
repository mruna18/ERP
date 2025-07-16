from django.db import models
from companies.models import Company

class CustomPermission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # e.g. 'sale_voucher'
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code

class Role(models.Model):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="roles")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)

    permissions = models.ManyToManyField(CustomPermission, blank=True)  # NEW

    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return self.name



class StaffProfile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=128)  # plain text: should ideally be hashed

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('username', 'company')

    def __str__(self):
        return f"{self.username} ({self.company.name})"

