from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=30)

    def __str__(self):
        return self.name

