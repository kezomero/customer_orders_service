from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCAuthenticationCallbackView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .services.sms import SMSService
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


# OIDC Callback View - Customizing token generation on successful login
class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        user = request.user
        print(user)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            # "first_name": user.first_name,
            # "last_name": user.last_name,
            # "code_id": getattr(user, "code_id", None),
        }

        return JsonResponse({
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "user": user_data,
        })


# Custom Login View to initiate OIDC authentication
class CustomLoginView(OIDCAuthenticationRequestView):
    def get(self, request, *args, **kwargs):
        self.success_url = request.build_absolute_uri(reverse("oidc_authentication_callback"))
        return super().get(request, *args, **kwargs)
    
def logout_view(request):
    # Log out of Django
    user = request.user
    if user.is_authenticated:
        # Blacklist all refresh tokens for this user
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                continue

    django_logout(request)

    # Build the OIDC provider logout URL
    params = {
        'redirect_uri': request.build_absolute_uri('/api/oidc/login/')
    }
    logout_url = f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urlencode(params)}"

    return redirect(logout_url)


# ViewSet for Customers
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def list(self, request, *args, **kwargs):
        customers = self.get_queryset()
        serializer = self.get_serializer(customers, many=True)
        return Response({'customers': serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            customer = self.get_object()
            serializer = self.get_serializer(customer)
            return Response({'customer': serializer.data}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'message': 'Customer created successfully.', 'customer': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

# ViewSet for Orders
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            error_detail = serializer.errors
            customer_id = request.data.get('customer')

            if 'customer' in error_detail and customer_id:
                if not Customer.objects.filter(pk=customer_id).exists():
                    return Response(
                        {'error': f"Customer with ID {customer_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response({'error': error_detail}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({
            'message': 'Order created successfully.',
            'order': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

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

        success = SMSService.send_order_notification(customer.phone, message)
        print(f"SMS {'sent' if success else 'failed'} for Order #{order.id}")

