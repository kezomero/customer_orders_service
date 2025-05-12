# api/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Customer, Order
from unittest.mock import patch
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from .admin import CustomerAdmin, OrderAdmin
from api.services.sms import SMSService
from rest_framework import serializers

class CustomerModelTests(TestCase):
    def test_customer_string_representation(self):
        customer = Customer(name="Test Customer", code="TEST123")
        self.assertEqual(str(customer), "Test Customer (TEST123)")

    def test_customer_model_fields(self):
        Customer.objects.create(
            name="Full Fields",
            code="FULL123",
            email="full@example.com",
            phone="+254712345678",
            location="Nairobi"
        )
        customer = Customer.objects.get(code="FULL123")
        self.assertEqual(customer.location, "Nairobi")

class OrderModelTests(TestCase):
    def test_order_string_representation(self):
        customer = Customer.objects.create(name="Test Customer", code="TEST123")
        order = Order.objects.create(
            customer=customer,
            item="Test Item",
            quantity=2,
            amount=100
        )
        self.assertEqual(str(order), f"Order #{order.id} - Test Item x2")

    def test_total_cost_property(self):
        customer = Customer.objects.create(name="Test Customer", code="TEST123")
        order = Order.objects.create(
            customer=customer,
            item="Test Item",
            quantity=3,
            amount=150
        )
        self.assertEqual(order.total_cost, 450)

class CustomerSerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.CharField()
    phone = serializers.CharField()

    def validate_phone(self, value):
        if value.startswith('0') and len(value) == 10:
            return '+254' + value[1:]
        if value.startswith('+254') and len(value) == 13:
            return value
        raise serializers.ValidationError("Invalid phone number format.")
class CustomerAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomerAdmin(Customer, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, 
                        ('name', 'code', 'email', 'phone', 'location', 'joined_at'))

class OrderAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = OrderAdmin(Order, self.site)
        self.customer = Customer.objects.create(name="Test", code="TST")
        self.order = Order.objects.create(
            customer=self.customer,
            item="Test Item",
            quantity=2,
            amount=100
        )

    def test_total_cost_display(self):
        self.assertEqual(self.admin.total_cost(self.order), 200)

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
        order = Order.objects.create(customer=self.customer, item='Test Item', amount=100, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order']['item'], 'Test Item')

    @patch('api.services.sms.SMSService.send_order_notification')
    def test_update_order(self, mock_sms):
        order = Order.objects.create(customer=self.customer, item='Test Item', amount=100, quantity=2)
        url = reverse('order-detail', args=[order.id])
        updated_data = self.order_data.copy()
        updated_data['quantity'] = 5
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order']['quantity'], 5)
        mock_sms.assert_called_once()

    def test_delete_order(self):
        order = Order.objects.create(customer=self.customer, item='Test Item', amount=100, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_order_calculation(self):
        order = Order.objects.create(customer=self.customer, item='Test', amount=200, quantity=3)
        self.assertEqual(order.total_cost, 600)
    
    def test_order_filtering_by_customer(self):
        customer2 = Customer.objects.create(name="Customer 2", code="CST2")
        Order.objects.create(customer=self.customer, item="Item 1", amount=100)
        Order.objects.create(customer=customer2, item="Item 2", amount=200)
        response = self.client.get(self.url, {'customer_id': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['item'], 'Item 1')

    def test_order_update_without_changes(self):
        order = Order.objects.create(customer=self.customer, item='Test Item', amount=100, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.put(url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SMSServiceTests(TestCase):
    @patch('africastalking.SMS.send', create=True)
    def test_send_sms_success(self, mock_send):
        mock_send.return_value = {
            'SMSMessageData': {
                'Recipients': [{'status': 'Success'}]
            }
        }
        result = SMSService.send_order_notification('0712345678', 'Test message')
        self.assertTrue(result)