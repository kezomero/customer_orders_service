from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCAuthenticationCallbackView
from django.http import JsonResponse
from django.urls import reverse

from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .services.sms import SMSService


# Custom OIDC Callback View
class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        user = request.user
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })


# Custom OIDC Login View
class CustomLoginView(OIDCAuthenticationRequestView):
    def get(self, request, *args, **kwargs):
        self.success_url = request.build_absolute_uri(reverse("oidc_authentication_callback"))
        return super().get(request, *args, **kwargs)


# ViewSet for Customers
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# ViewSet for Orders with SMS notification
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

        print(f"Prepared SMS: {message}")
        success = SMSService.send_order_notification(customer.phone, message)

        if success:
            print(f"SMS sent successfully for Order #{order.id}")
        else:
            print(f"Failed to send SMS for Order #{order.id}")
