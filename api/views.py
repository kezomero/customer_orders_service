from rest_framework import viewsets
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .services.sms import SMSService
import logging

logger = logging.getLogger(__name__)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        customer = order.customer
        total_cost = order.amount * order.quantity

        message = (
            f"Dear {customer.name},\n"
            f"Thank you for your order (#{order.id}) of {order.item} x{order.quantity}.\n"
            f"Total: KES {total_cost:.2f}\n"
            f"Payment Method: {order.payment_method}\n"
            f"We’ll contact you shortly."
        )

        logger.debug(f"Prepared SMS: {message}")

        success = SMSService.send_order_notification(customer.phone, message)

        if success:
            logger.info(f"SMS sent successfully for Order #{order.id}")
        else:
            logger.error(f"Failed to send SMS for Order #{order.id}")
