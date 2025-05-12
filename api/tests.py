from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer, Order
from unittest.mock import patch
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# CUSTOMER TESTS
class CustomerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.customer_data = {
            'name': 'Test Customer',
            'code': 'TEST123',
            'email': 'test@example.com',
            'phone': '+254712345678'
        }
        self.url = reverse('customer-list')

    def test_create_customer(self):
        response = self.client.post(self.url, self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

    def test_list_customers(self):
        Customer.objects.create(**self.customer_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['customers']), 1)

    def test_retrieve_customer(self):
        customer = Customer.objects.create(**self.customer_data)
        url = reverse('customer-detail', args=[customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer']['name'], 'Test Customer')

    def test_update_customer(self):
        customer = Customer.objects.create(**self.customer_data)
        url = reverse('customer-detail', args=[customer.id])
        updated_data = self.customer_data.copy()
        updated_data['name'] = 'Updated'
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer']['name'], 'Updated')

    def test_delete_customer(self):
        customer = Customer.objects.create(**self.customer_data)
        url = reverse('customer-detail', args=[customer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

# ORDER TESTS
class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name='Test Customer', email='test@example.com', phone='+254712345678')
        self.order_data = {
            'customer': self.customer.id,
            'item': 'Test Item',
            'amount': 100,
            'quantity': 2,
            'payment_method': 'M-Pesa'
        }
        self.url = reverse('order-list')

    def test_create_order(self):
        response = self.client.post(self.url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_list_orders(self):
        Order.objects.create(customer=self.customer, item='Item', amount=100, quantity=1, payment_method='Cash')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['orders']), 1)

    def test_retrieve_order(self):
        order = Order.objects.create(**self.order_data)
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order']['item'], 'Test Item')

    @patch('api.services.sms.SMSService.send_order_notification')
    def test_update_order(self, mock_sms):
        order = Order.objects.create(**self.order_data)
        url = reverse('order-detail', args=[order.id])
        updated_data = self.order_data.copy()
        updated_data['quantity'] = 5
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order']['quantity'], 5)
        mock_sms.assert_called_once()

    def test_delete_order(self):
        order = Order.objects.create(**self.order_data)
        url = reverse('order-detail', args=[order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_customer_on_order(self):
        bad_data = self.order_data.copy()
        bad_data['customer'] = 9999
        response = self.client.post(self.url, bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_calculation(self):
        order = Order.objects.create(customer=self.customer, item='Test', amount=200, quantity=3)
        self.assertEqual(order.total_cost, 600)

# SMS SERVICE TESTS
class SMSServiceTests(TestCase):
    @patch('africastalking.SMS.send', create=True)
    def test_send_sms_success(self, mock_send):
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [{'status': 'Success'}]
            }
        }
        from api.services.sms import SMSService
        result = SMSService.send_order_notification('+254712345678', 'Hello')
        self.assertTrue(result)

    def test_format_phone_number(self):
        from api.services.sms import SMSService
        cases = [
            ('0712345678', '+254712345678'),
            ('254712345678', '+254712345678'),
            ('+254712345678', '+254712345678'),
            ('invalid', None)
        ]
        for raw, expected in cases:
            self.assertEqual(SMSService._format_phone_number(raw), expected)

