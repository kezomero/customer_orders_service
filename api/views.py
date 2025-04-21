from rest_framework import viewsets
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .services.sms import SMSService
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCAuthenticationCallbackView
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.http import JsonResponse

# OIDC Callback View - Customizing token generation on successful login
class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    def get(self, request, *args, **kwargs):
        # Perform the default OIDC callback behavior
        response = super().get(request, *args, **kwargs)

        # Log the user details after authentication
        user = request.user
        
        # Assuming user name is composed of first and last name
        # You can also log a custom 'code_id' if you have this field in your user model
        code_id = getattr(user, 'code_id', 'No code id available')  # Default value if code_id doesn't exist

        # Generate the tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Return the tokens in the response
        return JsonResponse({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
        })

# Custom Login View to initiate OIDC authentication and redirect to the callback URL
class CustomLoginView(OIDCAuthenticationRequestView):
    def get(self, request, *args, **kwargs):
        # Corrected the reverse URL name
        self.success_url = request.build_absolute_uri(reverse("oidc_authentication_callback"))
        return super().get(request, *args, **kwargs)


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

        print(f"Prepared SMS: {message}")

        success = SMSService.send_order_notification(customer.phone, message)

        if success:
            print(f"SMS sent successfully for Order #{order.id}")
        else:
            logger.error(f"Failed to send SMS for Order #{order.id}")
