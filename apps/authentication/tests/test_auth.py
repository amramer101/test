import uuid
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.authentication.domain.models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("api:v1:register")
        self.login_url = reverse("api:v1:login")
        self.email = "testuser@example.com"
        self.password = "TestPassword123!"

    def test_user_registration(self):
        response = self.client.post(
            self.register_url,
            {"email": self.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], self.email)

    def test_user_login(self):
        # Register first
        User.objects.create_user(email=self.email, password=self.password)
        response = self.client.post(
            self.login_url,
            {"email": self.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {"email": self.email, "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
