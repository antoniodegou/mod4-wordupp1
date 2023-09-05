from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from subscription.forms import CustomUserCreationForm  # Replace 'your_app_name' with the name of your app

# Create your tests here.
class RegistrationPageTests(TestCase):

    def test_form_validity(self):
        form = CustomUserCreationForm({
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'securepassword1',
            'password2': 'securepassword1',
        })
        self.assertTrue(form.is_valid())

    def test_form_error(self):
        form = CustomUserCreationForm({
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'securepassword1',
            'password2': 'differentpassword',
        })
        self.assertFalse(form.is_valid())

    def test_create_user(self):
        self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'securepassword1',
            'password2': 'securepassword1',
        })
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_duplicate_username(self):
        get_user_model().objects.create_user('testuser', 'test@test.com', 'securepassword1')
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test2@test.com',
            'password1': 'securepassword1',
            'password2': 'securepassword1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')

    def test_redirect_on_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'securepassword1',
            'password2': 'securepassword1',
        })
        self.assertRedirects(response, reverse('dashboard'))  # Replace 'dashboard' with the name of your success URL
