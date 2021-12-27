from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from task_manager.mixins import TestCaseWithoutRollbar


class TestModelCase(TestCaseWithoutRollbar):
    """Test model case."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.credentials = {'username': 'testing_user'}
        cls.user_model = get_user_model()

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.user_model.objects.create(**self.credentials)

    def test_create(self):
        """Test check create model."""
        user = self.user_model.objects.get(**self.credentials)
        self.assertTrue(isinstance(user, self.user_model))
        self.assertEqual(self.credentials['username'], user.username)

        with self.assertRaises(TypeError):
            self.user_model.objects.create_user()

        with self.assertRaises(ValueError):
            self.user_model.objects.create_user(username='')

    def test_update(self):
        """Test check update model."""
        user = self.user_model.objects.get(**self.credentials)
        update_name = 'another_name'
        user.username = update_name
        user.save()
        self.assertEqual(update_name, user.username)

    def test_delete(self):
        """Test check delete model."""
        user = self.user_model.objects.get(**self.credentials)
        user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.user_model.objects.get(pk=user.id)
