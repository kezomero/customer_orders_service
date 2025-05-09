from rest_framework import serializers
from .models import Customer, Order
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework.exceptions import ValidationError

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'code', 'email', 'phone', 'location', 'joined_at']
        extra_kwargs = {
            'code': {'min_length': 3},
            'phone': {'min_length': 10}
        }

    def validate_phone(self, value):
        try:
            # Parse the phone number using the phonenumbers library
            phone_number = phonenumbers.parse(value)

            # Check if the number is valid
            if not phonenumbers.is_valid_number(phone_number):
                raise serializers.ValidationError("Phone number is not valid.")

            # Format the phone number in E.164 format (e.g., +254712345678 or +1XXX5551234)
            formatted_phone = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            return formatted_phone

        except NumberParseException:
            raise serializers.ValidationError("Phone number must be a valid international number.")
        except Exception as e:
            raise serializers.ValidationError(str(e))


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'item', 'quantity', 'amount', 'payment_method', 'created_at']
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)

        # Check if customer exists
        customer_id = data.get('customer')
        if customer_id:
            try:
                Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                raise ValidationError({'customer': f'Customer with ID {customer_id} does not exist.'})

        return validated_data