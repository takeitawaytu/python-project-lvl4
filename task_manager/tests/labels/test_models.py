from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from task_manager.labels.models import Label
from task_manager.mixins import TestCaseWithoutRollbar


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
