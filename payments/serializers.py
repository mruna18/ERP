from rest_framework import serializers
from .models import *

class PaymentInSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIn
        fields = '__all__'


class PaymentOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOut
        fields = '__all__'
