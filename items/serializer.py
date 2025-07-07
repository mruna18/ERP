from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantity = serializers.IntegerField(min_value=0)
    unit = serializers.ChoiceField(choices=[('pcs', 'Pieces'), ('kg', 'Kilogram'), ('ltr', 'Litre'), ('box', 'Box'), ('unit', 'Unit')])
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sales_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_applied = serializers.BooleanField()
    tax_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

    def validate_code(self, value):
        if Item.objects.filter(code=value).exists():
            raise serializers.ValidationError("Item with this code already exists.")
        return value

    def validate(self, attrs):
        if attrs.get("tax_applied") and not attrs.get("tax_percent"):
            raise serializers.ValidationError("Tax percent is required when tax is applied.")
        return attrs
