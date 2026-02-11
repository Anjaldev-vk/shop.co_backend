from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class LogoutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            name='Test User',
            is_verified=True
        )
        self.client = APIClient()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.refresh_url = reverse('token_refresh')

    def test_logout_blacklists_token(self):
        # 1. Login
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get refresh token from cookie
        refresh_token = response.cookies.get('refresh_token').value
        self.assertIsNotNone(refresh_token)
        
        # Set the cookie for the client (browser simulation)
        self.client.cookies['refresh_token'] = refresh_token
        
        # Authenticate for logout (requires IsAuthenticated)
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 2. Logout
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Verify cookie is deleted
        self.assertEqual(logout_response.cookies['refresh_token'].value, '')

        # 3. Verify Token is Blacklisted
        # Try to refresh using the old token
        self.client.cookies['refresh_token'] = refresh_token
        refresh_response = self.client.post(self.refresh_url)
        
        # Should fail because token is blacklisted
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
