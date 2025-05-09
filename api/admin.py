from django.contrib import admin
from .models import Customer, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'location', 'joined_at')
    search_fields = ('name', 'code', 'email', 'phone')
    list_filter = ('joined_at',)
    ordering = ('-joined_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'item', 'quantity', 'amount', 'total_cost', 'payment_method', 'created_at')
    search_fields = ('customer__name', 'item', 'payment_method')
    list_filter = ('payment_method', 'created_at')
    ordering = ('-created_at',)

    def total_cost(self, obj):
        return obj.total_cost
    total_cost.short_description = 'Total Cost'
