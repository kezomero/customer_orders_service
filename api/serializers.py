from rest_framework import serializers
from .models import Customer, Order

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'code', 'email', 'phone', 'location', 'joined_at']
        extra_kwargs = {
            'code': {'min_length': 3},
            'phone': {'min_length': 10}
        }

    def validate_phone(self, value):
        if value.startswith('07'):
            return '+254' + value[1:]
        elif value.startswith('254'):
            return '+' + value
        elif value.startswith('+254'):
            return value
        raise serializers.ValidationError("Phone number must be a valid Kenyan number.")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'item', 'quantity', 'amount', 'payment_method', 'created_at']
        read_only_fields = ['created_at']
