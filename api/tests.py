from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer, Order
from unittest.mock import patch
from django.contrib.auth.models import User

class CustomerTests(APITestCase):
    def setUp(self):
        self.customer_data = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'phone': '+254712345678'
        }
        self.url = reverse('customer-list')
        # Force authentication for customer tests if necessary
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_customer(self):
        response = self.client.post(self.url, self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

    def test_get_customers(self):
        Customer.objects.create(**self.customer_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class OrderTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            phone='+254712345678'
        )
        self.order_data = {
            'customer': self.customer.id,
            'item': 'Test Item',
            'amount': 100,
            'quantity': 2
        }
        self.url = reverse('order-list')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    @patch('api.services.sms.SMSService.send_order_notification')
    def test_create_order_with_sms(self, mock_sms):
        mock_sms.return_value = True
        response = self.client.post(self.url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_sms.called)
        
    def test_order_calculation(self):
        order = Order.objects.create(
            customer=self.customer,
            item='Test Item',
            amount=100,
            quantity=3
        )
        self.assertEqual(order.total_cost, 300)

class SMSServiceTests(TestCase):
    @patch('africastalking.SMS.send')
    def test_send_sms_success(self, mock_send):
        mock_send.return_value = {'SMSMessageData': {'Recipients': [{'status': 'Success'}]}}
        from api.services.sms import SMSService
        result = SMSService.send_order_notification('+254712345678', 'Test message')
        self.assertTrue(result)

    def test_phone_number_formatting(self):
        from api.services.sms import SMSService
        test_cases = [
            ('0712345678', '+254712345678'),
            ('254712345678', '+254712345678'),
            ('+254712345678', '+254712345678'),
            ('invalid', None)
        ]
        for input_phone, expected in test_cases:
            formatted = SMSService._format_phone_number(input_phone)
            self.assertEqual(formatted, expected)

class AuthenticationTests(APITestCase):
    @patch('mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get_token')
    def test_oidc_callback(self, mock_token):
        mock_token.return_value = {'access_token': 'test'}
        url = reverse('oidc_authentication_callback')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())

    def test_jwt_authentication(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)