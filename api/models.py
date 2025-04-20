from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal

# Regex for validating Kenyan phone numbers (optional but recommended)
phone_validator = RegexValidator(
    regex=r'^(\+?254|0)?\d{9}$',
    message='Enter a valid Kenyan phone number starting with 0 or +254 or 254.'
)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, validators=[phone_validator])

    def __str__(self):
        return f"{self.name} ({self.code})"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.item}"
