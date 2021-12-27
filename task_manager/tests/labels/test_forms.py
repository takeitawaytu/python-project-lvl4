from task_manager.labels.forms import LabelForm
from task_manager.mixins import TestCaseWithoutRollbar


class TestStatusCreationForm(TestCaseWithoutRollbar):
    """Test form validations."""

    def test_valid_form(self):
        """Test form is valid."""
        data = {'name': 'test'}
        self.assertTrue(LabelForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = {'name': ''}
        self.assertFalse(LabelForm(data=data).is_valid())
