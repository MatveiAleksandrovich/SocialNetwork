from django.contrib.auth import get_user_model
from django.forms.widgets import Select
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse


ABOUT_AUTHOR_URL = '/about/author/'
ABOUT_TECH_URL = '/about/tech/'


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_auth_page(self):
        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_about_auth_url_uses_correct_template(self):
        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_page(self):
        response = self.guest_client.get(ABOUT_TECH_URL)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_uses_correct_template(self):
        response = self.guest_client.get(ABOUT_TECH_URL)
        self.assertTemplateUsed(response, 'about/tech.html')
