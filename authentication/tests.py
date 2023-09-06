import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AuthenticationTestCase(TestCase):
    def test_user_registration(self):
        # Define a valid JSON payload for registration
        payload = {
            "username": "testuser",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }

        # Make a POST request to the registration endpoint
        response = self.client.post(reverse("register"), json.dumps(payload), content_type="application/json")

        # Expect a 200 status code for successful registration (adjust this based on your actual implementation)
        self.assertEqual(response.status_code, 200)  # Change this to the actual status code returned by your view

    def test_user_login(self):
        # Create a test user
        User.objects.create_user(username="testuser", password="testpassword123")

        # Define an invalid JSON payload for login
        payload = {
            "username": "testuser",
            "password": "incorrect_password",  # Invalid password
        }

        # Make a POST request to the login endpoint
        response = self.client.post(reverse("login"), json.dumps(payload), content_type="application/json")

        # Expect a 401 status code for unsuccessful login
        self.assertEqual(response.status_code, 401)

    def test_profile_api_authenticated(self):
        # Create a test user and log them in
        user = User.objects.create_user(username="testuser", password="testpassword123")
        self.client.login(username="testuser", password="testpassword123")

        # Make a GET request to the profile_api endpoint
        response = self.client.get(reverse("profile_api"))

        # Expect a 200 status code for successful profile retrieval
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the response data if needed

    def test_profile_api_unauthenticated(self):
        # Make a GET request to the profile_api endpoint without logging in
        response = self.client.get(reverse("profile_api"))

        # Expect a 401 status code for unauthenticated access
        self.assertEqual(response.status_code, 401)
        # Add more assertions to check the response data if needed

    def test_delete_user(self):
        # Create a test user and log them in
        user = User.objects.create_user(username="testuser", password="testpassword123")
        self.client.login(username="testuser", password="testpassword123")

        # Make a DELETE request to the delete_user endpoint
        response = self.client.delete(reverse("delete_user"))

        # Expect a 200 status code for successful user deletion
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the response data if needed
