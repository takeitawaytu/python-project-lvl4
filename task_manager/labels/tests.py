from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse
from task_manager.labels.forms import LabelForm
from task_manager.labels.models import Label


class TestModelCase(TestCase):
    """Test model case."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Label

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.model.objects.create(**self.data)

    def test_create(self):
        """Test check create model."""
        label = self.model.objects.get(**self.data)
        self.assertTrue(isinstance(label, self.model))
        self.assertEqual(self.data['name'], label.name)

    def test_update(self):
        """Test check update model."""
        label = self.model.objects.get(**self.data)
        update_label = 'another_name'
        label.username = update_label
        label.save()
        self.assertEqual(update_label, label.username)

    def test_delete(self):
        """Test check delete model."""
        label = self.model.objects.get(**self.data)
        label.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.model.objects.get(pk=label.id)

    def test_name_field_protection(self):
        """Test 'name' field protection."""
        label_in_db = self.model.objects.get(name='politic')
        with self.assertRaises(ProtectedError):
            label_in_db.delete()


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_labels = 15
        cls.model = Label
        cls.model.objects.bulk_create(
            [
                cls.model(
                    name=f'task{postfix}',  # noqa: WPS305
                ) for postfix in range(number_of_labels)
            ], batch_size=number_of_labels,
        )
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_view_url_exists_at_desired_location(self):
        """Test view url exists at desired location."""
        response = self.client.get('/labels/')
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_url_accessible_by_name(self):
        """Test view url accessible by name."""
        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'labels/index.html')

    def test_pagination_is_ten(self):
        """Test pagination is ten."""
        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['labels_list']) == 10)

    def test_lists_all_labels(self):
        """Test lists all labels."""
        response = self.client.get(
            '{url}?page=2'.format(url=reverse('labels')),
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['labels_list']) == 5)

    def test_not_auth_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('labels'))
        self.assertRedirects(response, reverse('login'))


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Label
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_label'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'labels/create.html')

        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertEqual(
            self.data['name'],
            self.model.objects.get(name=self.data['name']).name,
        )

    def test_cannot_create(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('labels'))
        count_labels = self.model.objects.all().count()

        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertEqual(count_labels, self.model.objects.all().count())

    def test_get_not_auth_users_cannot_create(self):
        """Test GET not authenticated users cannot create."""
        self.client.logout()
        response = self.client.get(reverse('create_label'))
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_create(self):
        """Test POST not authenticated users cannot create."""
        self.client.logout()
        response = self.client.post(reverse('create_label'))
        self.assertRedirects(response, reverse('login'))


class TestUpdateDeleteCase(TestCase):
    """Test update and delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Label
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.label = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        data_for_update = {'name': 'another_label'}
        response = self.client.post(
            path=reverse('update_label', args=[self.label.pk]),
            data=data_for_update,
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertEqual(
            data_for_update['name'],
            self.model.objects.get(pk=self.label.pk).name,
        )

    def test_cannot_update(self):
        """Test check unique field."""
        another_label_data = {'name': 'another_name'}
        another_label_created = self.model.objects.create(
            **another_label_data,
        )
        response = self.client.post(
            path=reverse('update_label', args=[another_label_created.pk]),
            data=self.data,
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_get_not_auth_users_cannot_update(self):
        """Test GET not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_update(self):
        """Test POST not authenticated users cannot update."""
        self.client.logout()
        response = self.client.post(
            reverse('update_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertFalse(
            self.model.objects.filter(name=self.data['name']).exists(),
        )

    def test_get_not_auth_users_cannot_delete(self):
        """Test GET not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_delete(self):
        """Test POST not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.post(
            reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))


class TestStatusCreationForm(TestCase):
    """Test form validations."""

    def test_valid_form(self):
        """Test form is valid."""
        data = {'name': 'test'}
        self.assertTrue(LabelForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = {'noname': 'test'}
        self.assertFalse(LabelForm(data=data).is_valid())
