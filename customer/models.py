from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    company_limit = models.PositiveIntegerField(default=3)  #default 3
    is_active = models.BooleanField(default=True) 
    selected_company = models.ForeignKey(
        'companies.Company',  # use app name for circular imports
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_by_customers',
        limit_choices_to={'is_active': True},
    )
    

    def __str__(self):
        return self.user.username

#! to select compnay
# class SelectedCompany(models.Model):
#     user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
#     company = models.ForeignKey('companies.Company', on_delete=models.DO_NOTHING)
#     updated_at = models.DateTimeField(auto_now=True)