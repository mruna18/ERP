from django.db import models
from django.contrib.auth.models import User
from companies.models import Company


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="job_roles")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class ModulePermission(models.Model):
    job_role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, related_name='permissions')
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="module_permissions")
    module_name = models.CharField(max_length=100)  # e.g., 'Sales Voucher', 'Inventory'

    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_view_specific = models.BooleanField(default=False)
    can_get_using_post = models.BooleanField(default=False)

    class Meta:
        unique_together = ('job_role', 'company', 'module_name')
        

    def __str__(self):
        return f"{self.job_role.name} - {self.module_name}"


class StaffProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_role = models.ForeignKey(Role, on_delete=models.CASCADE)

    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=128)  # store hashed passwords in production

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('username', 'company')

    def __str__(self):
        return f"{self.username} ({self.company.name})"
