from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.http.response import HttpResponseBase
from django.urls import reverse
from task_manager.mixins import TestCaseWithoutRollbar
from task_manager.statuses.models import Status
from task_manager.tasks.forms import TasksForm
from task_manager.tasks.models import Tasks
from task_manager.utils import load_file_from_fixture


class TestModelCase(TestCaseWithoutRollbar):
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
        cls.user_model = get_user_model()
        cls.tasks = load_file_from_fixture(
            filename='test_tasks.json',
            add_paths=['tasks'],
        )
        cls.users = load_file_from_fixture(
            filename='test_users.json',
            add_paths=['tasks'],
        )
        cls.user = cls.user_model.objects.get(
            username=cls.users['user_1']['username'],
        )
        cls.status = Status.objects.get(name='new')
        cls.task = Tasks.objects.get(
            name=cls.tasks['task_author_id_1']['name'],
        )

    def test_create(self):
        """Test check create model."""
        task_data = {
            'name': 'test',
            'status': self.status,
            'executor': self.user,
            'creator': self.user,
        }
        task_created = Tasks.objects.create(**task_data)
        task = Tasks.objects.get(pk=task_created.pk)
        self.assertTrue(isinstance(task, Tasks))
        self.assertEqual(task_data['name'], task.name)

    def test_update(self):
        """Test check update model."""
        task = Tasks.objects.get(pk=self.task.pk)
        update_name = 'another_name'
        task.name = update_name
        task.save()
        self.assertEqual(update_name, task.name)

    def test_status_field_protection(self):
        """Test 'status' field protection."""
        with self.assertRaises(ProtectedError):
            self.task.status.delete()

    def test_executor_field_protection(self):
        """Test 'executor' field protection."""
        with self.assertRaises(ProtectedError):
            self.task.executor.delete()

    def test_creator_field_protection(self):
        """Test 'creator' field protection."""
        with self.assertRaises(ProtectedError):
            self.task.creator.delete()

    def test_delete(self):
        """Test check delete model."""
        task = Tasks.objects.get(pk=self.task.pk)
        task.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Tasks.objects.get(pk=task.pk)


class TestListViewCase(TestCaseWithoutRollbar):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_tasks = 15
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user = cls.user_model.objects.create_user(**cls.credentials)
        cls.status = Status.objects.create(name='test_status')
        Tasks.objects.bulk_create(
            [
                Tasks(
                    name=f'task{postfix}',  # noqa: WPS305
                    status=cls.status,
                    creator=cls.user,
                    executor=cls.user,
                ) for postfix in range(number_of_tasks)
            ], batch_size=number_of_tasks,
        )

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_view_url_exists_at_desired_location(self):
        """Test view url exists at desired location."""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_url_accessible_by_name(self):
        """Test view url accessible by name."""
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'tasks/index.html')

    def test_pagination_is_ten(self):
        """Test pagination is ten."""
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['tasks_list']) == 10)

    def test_lists_all_tasks(self):
        """Test lists all tasks."""
        response = self.client.get(
            '{url}?page=2'.format(url=reverse('tasks')),
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['tasks_list']) == 5)

    def test_not_auth_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('tasks'))
        self.assertRedirects(response, reverse('login'))


class TestFilterViewCase(TestCaseWithoutRollbar):
    """Test filter view."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Tasks
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'user_test1', 'password': '12345'}
        cls.url = reverse('tasks')

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def get_absolute_filter_url(self, **kwargs) -> str:
        """
        Get absolute url use query string.
        Args:
            kwargs:
        Returns:
            str:
        """
        data = {'status': '', 'executor': '', 'label': ''}
        data.update(kwargs)
        query_str = '?status={status}&executor={executor}&label={label}'
        if 'creator' in kwargs:
            query_str = '{query_str}&self_tasks=on'.format(query_str=query_str)
        query_str = query_str.format(**data)
        return '{url}{query_str}'.format(url=self.url, query_str=query_str)

    def test_filters_by_each_field(self):
        """Test filters by each field."""
        mapping_fields_db = {
            'status': 'status',
            'executor': 'executor',
            'label': 'labels',
        }
        query_data = [('status', 3), ('executor', 1), ('label', 6)]
        for data in query_data:
            field, field_data = data
            count_rec_in_db = self.model.objects.filter(
                **{mapping_fields_db[field]: field_data},
            ).count()
            response = self.client.get(
                self.get_absolute_filter_url(**{field: field_data}),
            )
            self.assertEqual(response.status_code, HttpResponseBase.status_code)
            self.assertEqual(count_rec_in_db, len(response.context['tasks_list']))

    def test_filter_switch_on_off_task_only_author(self):
        """Test switch on/off task only author."""
        data = {'creator': 1}
        count_rec_switch_on = self.model.objects.filter(**data).count()
        response = self.client.get(self.get_absolute_filter_url(**data))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertEqual(count_rec_switch_on, len(response.context['tasks_list']))

        count_rec_switch_off = self.model.objects.all().count()
        response = self.client.get(self.get_absolute_filter_url())
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertEqual(count_rec_switch_off, len(response.context['tasks_list']))


class TestCreateViewCase(TestCaseWithoutRollbar):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.status = Status.objects.create(name='test_status')
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user = cls.user_model.objects.create_user(**cls.credentials)
        cls.data = {
            'name': 'test_task',
            'status': cls.status.pk,
            'creator': cls.user.pk,
            'executor': cls.user.pk,
        }

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_task'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'tasks/create.html')

        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertEqual(
            self.data['name'],
            Tasks.objects.get(name=self.data['name']).name,
        )

    def test_cannot_create(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('tasks'))
        count_tasks = Tasks.objects.all().count()

        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertEqual(count_tasks, Tasks.objects.all().count())

    def test_get_not_auth_users_cannot_create(self):
        """Test GET not authenticated users cannot create."""
        self.client.logout()
        response = self.client.get(reverse('create_status'))
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_create(self):
        """Test POST not authenticated users cannot create."""
        self.client.logout()
        response = self.client.post(reverse('create_status'))
        self.assertRedirects(response, reverse('login'))


class TestUpdateDeleteCase(TestCaseWithoutRollbar):
    """Test update and delete view."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'user_test1', 'password': '12345'}
        cls.data = load_file_from_fixture(
            filename='test_tasks.json',
            add_paths=['tasks'],
        )

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)
        self.task = Tasks.objects.get(
            name=self.data['task_author_id_1']['name'],
        )

    def test_update_view(self):
        """Test check view update model."""
        data = {
            'name': 'another_name',
            'executor': 1,
            'creator': 1,
            'status': 2,
        }
        response = self.client.post(
            path=reverse('update_task', args=[self.task.pk]),
            data=data,
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertEqual(
            data['name'],
            Tasks.objects.get(pk=self.task.pk).name,
        )

    def test_cannot_update(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('update_task', args=[self.task.pk]),
            data=self.data['task_author_id_2'],
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertNotEqual(
            self.data['task_author_id_2']['name'],
            Tasks.objects.get(pk=self.task.pk).name,
        )

    def test_get_not_auth_users_cannot_update(self):
        """Test GET not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_update(self):
        """Test not authenticated users cannot update."""
        self.client.logout()
        response = self.client.post(
            reverse('update_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertFalse(
            Tasks.objects.filter(
                name=self.data['task_author_id_1']['name'],
            ).exists(),
        )

    def test_get_not_auth_users_cannot_delete(self):
        """Test GET not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_delete(self):
        """Test POST not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.post(
            reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_only_the_author_can_delete(self):
        """Test only the author task can delete."""
        task_another_author = Tasks.objects.get(
            name=self.data['task_author_id_2']['name'],
        )
        response = self.client.post(
            reverse('delete_task', args=[task_another_author.pk]),
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertNotEqual(
            task_another_author.creator,
            self.task.creator,
        )
        self.assertTrue(
            Tasks.objects.filter(
                name=self.data['task_author_id_2']['name'],
            ).exists(),
        )


class TestStatusCreationForm(TestCaseWithoutRollbar):
    """Test form validations."""

    fixtures = ['tasks/db_users.json', 'tasks/db_statuses.json']

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.data = load_file_from_fixture(
            filename='test_users.json',
            add_paths=['tasks'],
        )
        cls.user = cls.user_model.objects.get(
            username=cls.data['user_1']['username'],
        )
        cls.status = Status.objects.get(name='new')
        cls.form_data = {
            'name': 'test',
            'description': 'test description',
            'status': cls.status,
            'executor': cls.user,
        }

    def test_valid_form(self):
        """Test form is valid."""
        self.assertTrue(TasksForm(data=self.form_data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        form_data = (
            {'name': '', 'status': '1', 'executor': '1'},
            {'name': 'test', 'status': '', 'executor': '1'},
            {'name': 'test', 'status': '1', 'executor': ''},
        )
        for data in form_data:
            self.assertFalse(TasksForm(data=data).is_valid())
