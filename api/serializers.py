from rest_framework import serializers
from .models import Customer, Order

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'code', 'phone']
        extra_kwargs = {
            'code': {'min_length': 3},
            'phone': {'min_length': 10}
        }

    def validate_phone(self, value):
        # Optional: normalize and reformat phone number
        if value.startswith('07'):
            value = '+254' + value[1:]
        elif value.startswith('254'):
            value = '+' + value
        elif not value.startswith('+254'):
            raise serializers.ValidationError("Phone number must be a valid Kenyan number.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'item', 'amount', 'created_at']
        read_only_fields = ['created_at']
