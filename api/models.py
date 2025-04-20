from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100, blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customers'  # Custom table name

    def __str__(self):
        return f"{self.name} ({self.code})"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(max_length=50, default="M-Pesa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'  # Custom table name

    def __str__(self):
        return f"Order #{self.id} - {self.item} x{self.quantity}"
