import logging
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
from .serializers import CustomerSerializer

logger = logging.getLogger(__name__)

class CustomerModelTests(TestCase):
    """Test Customer model functionality"""
    
    def setUp(self):
        print("\n=== Setting up Customer model tests ===")
        self.customer = Customer.objects.create(
            name="Test Customer",
            code="TEST123",
            email="test@example.com",
            phone="+254712345678",
            location="Nairobi"
        )

    def test_customer_creation(self):
        print("Testing customer creation...")
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(self.customer.code, "TEST123")
        print("✅ Customer creation test passed")

    def test_customer_string_representation(self):
        print("Testing customer string representation...")
        self.assertEqual(str(self.customer), "Test Customer (TEST123)")
        print("✅ Customer string representation test passed")


class OrderModelTests(TestCase):
    """Test Order model functionality"""
    
    def setUp(self):
        print("\n=== Setting up Order model tests ===")
        self.customer = Customer.objects.create(
            name="Order Customer",
            code="ORDER123"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            item="Test Item",
            amount=100.00,
            quantity=2
        )

    def test_order_creation(self):
        print("Testing order creation...")
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.item, "Test Item")
        print("✅ Order creation test passed")

    def test_order_string_representation(self):
        print("Testing order string representation...")
        expected = f"Order #{self.order.id} - Test Item x2"
        self.assertEqual(str(self.order), expected)
        print("✅ Order string representation test passed")

    def test_total_cost_calculation(self):
        print("Testing total cost calculation...")
        self.assertEqual(self.order.total_cost, 200.00)
        print("✅ Total cost calculation test passed")

    
class CustomerSerializerTests(TestCase):
    """Test Customer serializer validation"""
    
    def test_valid_phone_number(self):
        print("\nTesting valid phone number formats...")
        valid_numbers = [
            ('0712345678', '+254712345678'),
            ('+254712345678', '+254712345678'),
            ('254712345678', '+254712345678')
        ]
        
        for input_num, expected in valid_numbers:
            data = {'name': 'Test', 'code': 'TST', 'phone': input_num}
            serializer = CustomerSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Validation failed for phone number: {input_num}")  # Custom failure message
            self.assertEqual(serializer.validated_data['phone'], expected)
        print("✅ Valid phone number tests passed")

    def test_invalid_phone_number(self):
        print("Testing invalid phone number formats...")
        invalid_numbers = ['12345', '2547123456789', '07invalid']
        
        for number in invalid_numbers:
            data = {'name': 'Test', 'code': 'TST', 'phone': number}
            serializer = CustomerSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('phone', serializer.errors)
        print("✅ Invalid phone number tests passed")

class CustomerAPITests(APITestCase):
    """Test Customer API endpoints"""
    
    def setUp(self):
        print("\n=== Setting up Customer API tests ===")
        self.user = User.objects.create_user(
            username='api tester',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.customer_data = {
            'name': 'API Customer',
            'code': 'API123',
            'phone': '0712345678'
        }
        self.url = reverse('customer-list')

    def test_create_customer(self):
        print("Testing customer creation via API...")
        response = self.client.post(self.url, self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        print("✅ Customer creation via API test passed")

    
class OrderAPITests(APITestCase):
    """Test Order API endpoints"""
    
    def setUp(self):
        print("\n=== Setting up Order API tests ===")
        self.user = User.objects.create_user(
            username='order tester',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(
            name="Order Customer",
            code="ORDERCUST",
            phone="0712345678"
        )
        self.order_data = {
            'customer': self.customer.id,
            'item': 'API Test Item',
            'amount': 150.00,
            'quantity': 3
        }
        self.url = reverse('order-list')

    @patch('api.services.sms.SMSService.send_order_notification')
    def test_order_creation_with_sms(self, mock_sms):
        print("Testing order creation with SMS notification...")
        mock_sms.return_value = True

        expected_sms_message = (
            'Dear Order Customer,\n'
            'Thank you for your order (#3) of API Test Item x3.\n'
            'Total: KES 450.00\n'
            'Payment Method: M-Pesa\n'
            'We’ll contact you shortly.'
        )
        
        response = self.client.post(self.url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_sms.assert_called_once_with(
            self.customer.phone,
            expected_sms_message
        )
        print("✅ Order creation with SMS test passed")

    def test_order_filtering(self):
        print("Testing order filtering by customer...")
        # Create orders for different customers
        customer2 = Customer.objects.create(
            name="Another Customer",
            code="CUST002",
            phone="0722222222"
        )
        Order.objects.create(
            customer=self.customer,
            item="Filter Item 1",
            amount=100.00
        )
        Order.objects.create(
            customer=customer2,
            item="Filter Item 2",
            amount=200.00
        )
        
        response = self.client.get(self.url, {'customer_id': self.customer.id})
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['item'], 'Filter Item 1')
        print("✅ Order filtering test passed")

    def test_order_update(self):
        print("Testing order update functionality...")
        order = Order.objects.create(
            customer=self.customer,
            item="Original Item",
            amount=100.00
        )
        url = reverse('order-detail', args=[order.id])
        updated_data = {
            'item': 'Updated Item',
            'amount': 150.00,
            'customer': self.customer.id
        }
        
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.item, 'Updated Item')
        print("✅ Order update test passed")

class AdminInterfaceTests(TestCase):
    """Test Django admin interface customization"""
    
    def setUp(self):
        print("\n=== Setting up Admin interface tests ===")
        self.site = AdminSite()
        self.customer_admin = CustomerAdmin(Customer, self.site)
        self.order_admin = OrderAdmin(Order, self.site)
        
        self.customer = Customer.objects.create(
            name="Admin Customer",
            code="ADMIN123"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            item="Admin Item",
            amount=200.00,
            quantity=2
        )

    def test_customer_admin_list_display(self):
        print("Testing Customer admin list display...")
        self.assertEqual(
            self.customer_admin.list_display,
            ('name', 'code', 'email', 'phone', 'location', 'joined_at')
        )
        print("✅ Customer admin list display test passed")

    def test_order_admin_total_cost(self):
        print("Testing Order admin total cost display...")
        self.assertEqual(self.order_admin.total_cost(self.order), 400.00)
        print("✅ Order admin total cost test passed")

class SMSServiceTests(TestCase):
    """Test SMS service integration"""
    
    @patch('api.services.sms.africastalking.SMS.send')
    def test_successful_sms_delivery(self, mock_send):
        print("\nTesting successful SMS delivery...")
        mock_send.return_value = {
            'SMSMessageData': {'Recipients': [{'status': 'Success'}]}
        }
        
        result = SMSService.send_order_notification(
            '+254712345678',
            'Test message'
        )
        self.assertTrue(result)
        print("✅ SMS success test passed")

    @patch('api.services.sms.africastalking.SMS.send')
    def test_failed_sms_delivery(self, mock_send):
        print("Testing failed SMS delivery...")
        mock_send.side_effect = Exception("API Error")
        
        result = SMSService.send_order_notification(
            '+254712345678',
            'Test message'
        )
        self.assertFalse(result)
        print("✅ SMS failure test passed")

    @patch('api.services.sms.africastalking.SMS.send')
    def test_sms_service_logging(self, mock_send):
        print("Testing SMS service error logging...")
        mock_send.side_effect = Exception("Rate limit exceeded")

        with self.assertLogs('api.services.sms', level='ERROR') as cm:
            SMSService.send_order_notification('0712345678', 'Test message')

        self.assertIn("Rate limit exceeded", cm.output[0])
        print("✅ SMS logging test passed")
