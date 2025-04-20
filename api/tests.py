from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import Customer

class OrderAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(
            name="Test Customer",
            code="TC001",
            phone="+254700000000"
        )

    @patch('api.services.sms.SMSService.send_order_notification')
    def test_create_order_sends_sms(self, mock_sms):
        url = reverse('order-list')
        data = {
            'customer': self.customer.id,
            'item': 'Test Item',
            'amount': '1000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_sms.assert_called_once()