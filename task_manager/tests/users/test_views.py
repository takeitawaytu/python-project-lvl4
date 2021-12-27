from django.contrib.auth import get_user_model
from django.http.response import HttpResponseBase
from django.urls import reverse
from task_manager.mixins import TestCaseWithoutRollbar
from task_manager.utils import load_file_from_fixture


class TestListViewCase(TestCaseWithoutRollbar):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_users = 15
        cls.user_model = get_user_model()
        for postfix in range(number_of_users):
            user = {'username': 'user{postfix}'.format(postfix=postfix)}
            cls.user_model.objects.create(**user)

    def test_view_url_exists_at_desired_location(self):
        """Test view url exists at desired location."""
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_url_accessible_by_name(self):
        """Test view url accessible by name."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_pagination_is_ten(self):
        """Test pagination is ten."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['users_list']) == 10)

    def test_lists_all_users(self):
        """Test lists all users."""
        response = self.client.get(
            '{url}?page=2'.format(url=reverse('users')),
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['users_list']) == 5)


class TestCreateViewCase(TestCaseWithoutRollbar):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/create.html')

        user = self.users_data['user_insert']
        response = self.client.post(
            path=reverse('create_user'),
            data=user,
        )
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(
            user['username'],
            self.user_model.objects.get(username=user['username']).username,
        )


class TestLoginLogoutViewCase(TestCaseWithoutRollbar):
    """Test login and logout user."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.user = cls.users_data['user']
        cls.user_model.objects.create_user(**cls.user)

    def test_login(self):
        """Test login user."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/login.html')

        self.assertTrue(
            self.user_model.objects.filter(
                username=self.user['username'],
            ).exists(),
        )
        response = self.client.post(
            path=reverse('login'),
            data=self.user,
            follow=True,
        )
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        """Test logout user."""
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(response.context['user'].is_authenticated)


class TestUpdateDeleteCase(TestCaseWithoutRollbar):
    """Test update and delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.credentials = cls.users_data['user']
        cls.user = cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        response = self.client.post(
            path=reverse('update_user', args=[self.user.pk]),
            data=self.users_data['user_update'],
        )
        self.assertRedirects(response, reverse('users'))
        self.assertEqual(
            self.users_data['user_update']['username'],
            self.user_model.objects.get(pk=self.user.pk).username,
        )

    def test_try_update_another_user(self):
        """Test cannot update data another user."""
        user2 = self.user_model.objects.create(
            **self.users_data['user2'],
        )
        response = self.client.post(
            path=reverse('update_user', args=[user2.pk]),
            data=self.users_data['user_update'],
        )
        self.assertRedirects(response, reverse('users'))
        self.assertNotEqual(
            self.users_data['user_update']['username'],
            self.user_model.objects.get(pk=user2.pk).username,
        )

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_user', args=[self.user.pk]),
        )
        self.assertRedirects(response, reverse('users'))
        self.assertFalse(
            self.user_model.objects.filter(
                username=self.credentials['username'],
            ).exists(),
        )

    def test_try_delete_another_user(self):
        """Test cannot delete data another user."""
        user2 = self.user_model.objects.create(
            **self.users_data['user2'],
        )
        response = self.client.post(
            path=reverse('delete_user', args=[user2.pk]),
        )
        self.assertRedirects(response, reverse('users'))
        self.assertTrue(
            self.user_model.objects.filter(
                username=user2.username,
            ).exists(),
        )
