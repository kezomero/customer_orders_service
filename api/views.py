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
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

# OIDC Callback View - Customizing token generation on successful login
class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        user = request.user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Customize user data returned in the response
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            # Add custom fields like 'code_id' if needed
            "code_id": getattr(user, "code_id", None),
        }

        return JsonResponse({
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "user": user_data,
        })

# Custom Login View to initiate OIDC authentication and redirect to the callback URL
class CustomLoginView(OIDCAuthenticationRequestView):
    def get(self, request, *args, **kwargs):
        self.success_url = request.build_absolute_uri(reverse("oidc_authentication_callback"))
        return super().get(request, *args, **kwargs)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            error_detail = serializer.errors

            # Customize error for non-existent customer
            customer_id = request.data.get('customer')
            if 'customer' in error_detail and customer_id:
                try:
                    Customer.objects.get(pk=customer_id)
                except Customer.DoesNotExist:
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