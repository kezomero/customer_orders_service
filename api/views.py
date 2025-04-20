from rest_framework import viewsets
from rest_framework.response import Response
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .services.sms import SMSService
import logging  # Add this import

# Set up logging
logger = logging.getLogger(__name__)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        message = f"New order: {order.item} (Amount: {order.amount})"
        
        # Log the message that will be sent
        logger.debug(f"Sending SMS with message: {message}")
        
        # Send the notification to the customer via SMS
        success = SMSService.send_order_notification(
            order.customer.phone,
            message
        )
        
        if success:
            logger.info(f"SMS notification sent for order {order.id} to {order.customer.phone}")
        else:
            logger.error(f"Failed to send SMS notification for order {order.id} to {order.customer.phone}")
