from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse
from task_manager.statuses.forms import StatusForm
from task_manager.statuses.models import Status


class TestModelCase(TestCase):
    """Test model case."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Status

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.model.objects.create(**self.data)

    def test_create(self):
        """Test check create model."""
        status = self.model.objects.get(**self.data)
        self.assertTrue(isinstance(status, self.model))
        self.assertEqual(self.data['name'], status.name)

    def test_update(self):
        """Test check update model."""
        status = self.model.objects.get(**self.data)
        update_status = 'another_name'
        status.username = update_status
        status.save()
        self.assertEqual(update_status, status.username)

    def test_delete(self):
        """Test check delete model."""
        status = self.model.objects.get(**self.data)
        status.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.model.objects.get(pk=status.id)


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_status = 15
        cls.model = Status
        for postfix in range(number_of_status):
            status = {'name': 'status{postfix}'.format(postfix=postfix)}
            cls.model.objects.create(**status)

        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_view_url_exists_at_desired_location(self):
        """Test view url exists at desired location."""
        response = self.client.get('/statuses/')
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_url_accessible_by_name(self):
        """Test view url accessible by name."""
        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'statuses/index.html')

    def test_pagination_is_ten(self):
        """Test pagination is ten."""
        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['statuses_list']) == 10)

    def test_lists_all_users(self):
        """Test lists all users."""
        response = self.client.get(
            '{url}?page=2'.format(url=reverse('statuses')),
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['statuses_list']) == 5)

    def test_not_authenticated_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('statuses'))
        self.assertRedirects(response, reverse('login'))


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Status
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_status'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'statuses/create.html')

        response = self.client.post(
            path=reverse('create_status'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertEqual(
            self.data['name'],
            self.model.objects.get(name=self.data['name']).name,
        )

    def test_not_authenticated_users_cannot_create(self):
        """Test not authenticated users cannot create."""
        self.client.logout()
        response = self.client.get(reverse('create_status'))
        self.assertRedirects(response, reverse('login'))


class TestUpdateDeleteCase(TestCase):
    """Test update and delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Status
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.status = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        data_for_update = {'name': 'another_status'}
        response = self.client.post(
            path=reverse('update_status', args=[self.status.pk]),
            data=data_for_update,
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertEqual(
            data_for_update['name'],
            self.model.objects.get(pk=self.status.pk).name,
        )

    def test_not_authenticated_users_cannot_update(self):
        """Test not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertFalse(
            self.model.objects.filter(name=self.data['name']).exists(),
        )

    def test_not_authenticated_users_cannot_delete(self):
        """Test not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))


class TestStatusCreationForm(TestCase):
    """Test form validations."""

    def test_valid_form(self):
        """Test form is valid."""
        data = {'name': 'test'}
        self.assertTrue(StatusForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = {'noname': 'test'}
        self.assertFalse(StatusForm(data=data).is_valid())
