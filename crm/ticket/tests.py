from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ticket.models import Ticket

User = get_user_model()

class CreateTicketAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
        
        # URL for creating a ticket
        self.url = reverse('ticket:create-ticket')
        
    def test_create_ticket_success(self):
        """Test creating a ticket with valid data"""
        data = {
            'name': 'Test Ticket',
            'description': 'This is a test ticket',
            'source': 'email',  
            'phone_number': '+1234567890'
        }
        
        print("Sending data:", data)  
        response = self.client.post(self.url, data, format='json')
        print("Response status:", response.status_code)  
        print("Response data:", response.data)  
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Ticket created successfully')
        self.assertIn('data', response.data)
        
        # Check the ticket was created in the database
        ticket = Ticket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.name, 'Test Ticket')
        self.assertEqual(ticket.owner, self.user)
        self.assertEqual(ticket.source, 'email')  
        self.assertEqual(ticket.status, 'new')  

    def test_create_ticket_missing_required_fields(self):
        """Test creating a ticket with missing required fields"""
        data = {
            'name': 'Incomplete Ticket',
            # Missing description and source
            'priority': 'medium'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)
        self.assertIn('description', response.data['errors'])
        self.assertIn('source', response.data['errors'])
        
    def test_create_ticket_unauthenticated(self):
        """Test that unauthenticated users cannot create tickets"""
        self.client.force_authenticate(user=None)  # Log out
        
        data = {
            'name': 'Unauthenticated Ticket',
            'description': 'This should fail',
            'source': 'web',
            'priority': 'low'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Should return 401 Unauthorized or 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
