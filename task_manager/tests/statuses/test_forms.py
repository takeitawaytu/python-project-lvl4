from task_manager.mixins import TestCaseWithoutRollbar
from task_manager.users.forms import CustomUserCreationForm
from task_manager.utils import load_file_from_fixture


class TestCustomUserCreationForm(TestCaseWithoutRollbar):
    """Test form validations."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )

    def test_valid_form(self):
        """Test form is valid."""
        data = self.users_data['valid_form']
        self.assertTrue(CustomUserCreationForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = self.users_data['invalid_form']
        self.assertFalse(CustomUserCreationForm(data=data).is_valid())
