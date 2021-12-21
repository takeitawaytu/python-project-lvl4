from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse


class TestI18nCase(TestCase):
    """Language tests."""

    def test_i18_ru(self):
        """Test correct get language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'ru'}
        name_project = 'Менеджер задач'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))

    def test_i18_en(self):
        """Test correct get language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        name_project = 'Task Manager'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))
