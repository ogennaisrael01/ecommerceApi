from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserManagementTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            email="ogenna@test.gmail.com",
            password="0987poiu",
            first_name="ogenna",
            last_name="israel",
            username="ogenna01",
            )
        self.user.is_active =True
        self.user.save()
        

        """ Setup for user registration and login"""
        self.registration_url = "/auth/sign-up/"
        self.registration_data = {
                            "email": "og@test.gmail.com",
                            "first_name": "ogennatest",
                            "last_name": "testogenna",
                            "username": "19928ogenna",
                            "password": "0987poiu",
                            "confirm_password": "0987poiu"
                        }

        # setup login endpoint
        # = Get the registered user instance
        self.login_url = "/auth/sign-in/"
        self.login_data = {
                    "email": self.user.email,
                    "password": "0987poiu"
        }

        # Email vefification 
        self.verification_data = {
                            "code": "843366"
                        }
        self.verification_url = "/auth/verify/email/"

    def test_registration(self):
        response = self.client.post(self.registration_url, self.registration_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        response = self.client.post(self.login_url, self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_creation(self):
        get_object = User.objects.get(email="ogenna@test.gmail.com")
        self.assertEqual(get_object.email, self.user.email)
        self.assertEqual(get_object.first_name, "ogenna")
        

    def test_email_verificatil(self):
        response = self.client.post(self.verification_url, self.verification_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)