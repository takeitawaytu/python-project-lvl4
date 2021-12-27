from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from task_manager.mixins import TestCaseWithoutRollbar
from task_manager.statuses.models import Status
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
