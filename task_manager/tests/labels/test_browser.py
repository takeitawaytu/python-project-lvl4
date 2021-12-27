import os
import re
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from task_manager.utils import load_file_from_fixture


class TestBrowserHeadless(StaticLiveServerTestCase):
    """Behavior test."""

    fixtures = [
        'browser/db_users.json',
        'browser/db_statuses.json',
        'browser/db_labels.json',
        'browser/db_tasks.json',
    ]

    port = 8001

    @classmethod
    def setUpClass(cls):
        """Run once to set up non-modified data for all class methods."""
        super().setUpClass()
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.data = load_file_from_fixture(
            filename='test_data.json',
            add_paths=['browser'],
        )

    @classmethod
    def tearDownClass(cls):
        """Run once to close the handles."""
        cls.browser.close()
        cls.playwright.stop()
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'false'
        super().tearDownClass()

    def get_absolute_url(self, path: str = '') -> str:
        """
        Get absolute url to current live server.
        Args:
            path:
        Returns:
            str:
        """
        return urljoin(self.live_server_url, path)

    def setUp(self):
        """Run once for every test method to setup clean data."""
        self.page = self.browser.new_page()

    def tearDown(self):
        """Run once for every test method to close the handles."""
        self.page.close()

    def login(self, credentials):
        """Login."""
        self.page.goto(self.get_absolute_url('/'))
        self.page.click('text="Вход"')
        self.page.wait_for_load_state()

        self.page.fill('input[name="username"]', credentials['username'])
        self.page.fill('input[name="password"]', credentials['password'])
        self.page.click('text="Войти"')
        self.page.wait_for_load_state()

    def test_index_no_auth(self):
        """Test cannot view if user no auth."""
        self.page.goto(self.get_absolute_url('/'))
        assert self.page.query_selector('text="Метки"') is None

        self.page.goto(self.get_absolute_url('/labels/'))
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

    def test_index(self):
        """Test index."""
        data = self.data['first']['user']
        self.login(data)

        assert self.page.query_selector('text="Метки"') is not None

        self.page.click('text="Метки"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/labels/')
        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['labels']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['labels']['name'],
        )

        assert self.page.query_selector(row1) is not None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector('text="Создать метку"') is not None

    def test_create(self):
        """Test create."""
        data = self.data['first']['user']
        self.login(data)
        self.page.goto(self.get_absolute_url('/labels/create/'))

        assert self.page.url == self.get_absolute_url('/labels/create/')
        assert self.page.get_attribute('#id_name', 'value') is None

        self.page.fill('input[name="name"]', 'test')
        self.page.click('text=Создать')
        self.page.wait_for_load_state()
        assert re.search(
            'Метка успешно создана',
            self.page.text_content('.alert'),
        )
        assert self.page.url == self.get_absolute_url('/labels/')

    def test_update(self):
        """Test update."""
        data = self.data['first']
        self.login(data['user'])

        self.page.click('text="Метки"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(text=data['labels']['name'])
        row = self.page.query_selector(row1)
        assert row is not None
        row.query_selector('text="Изменить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/labels/\d+/update/', self.page.url)
        assert self.page.get_attribute('#id_name', 'value') == data['labels']['name']

        data_upd = 'test'
        self.page.fill('input[name="name"]', data_upd)

        self.page.click('text="Изменить"')
        self.page.wait_for_load_state()
        assert self.page.url == self.get_absolute_url('/labels/')
        assert re.search(
            'Метка успешно изменена',
            self.page.text_content('.alert'),
        )

        row_upd = '*css=tr >> text={text}'.format(text=data_upd)
        assert self.page.query_selector(row_upd) is not None

    def test_cannot_update_no_auth(self):
        """Test cannot update if user no auth"""
        self.page.goto(self.get_absolute_url('/labels/42/update/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

    def test_delete(self):
        """Test delete."""
        data = self.data['first']['user']
        self.login(data)

        self.page.click('text="Метки"')
        self.page.wait_for_load_state()

        status_data = self.data['fourth']['labels']

        row1 = '*css=tr >> text={text}'.format(text=status_data['name'])
        row = self.page.query_selector(row1)
        assert row is not None
        row.query_selector('text="Удалить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/labels/\d+/delete/', self.page.url)
        self.page.click('text="Да, удалить"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/labels/')
        assert re.search(
            'Метка успешно удалена',
            self.page.text_content('.alert'),
        )

    def test_cannot_delete_no_auth(self):
        """Test cannot delete if user no auth"""
        self.page.goto(self.get_absolute_url('/labels/42/delete/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

    def test_cannot_delete_if_using_in_tasks(self):
        """Test cannot delete if using in tasks."""
        data = self.data['first']
        self.login(data['user'])

        self.page.click('text="Метки"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(text=data['labels']['name'])
        row = self.page.query_selector(row1)
        assert row is not None
        row.query_selector('text="Удалить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/labels/\d+/delete/', self.page.url)
        self.page.click('text="Да, удалить"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/labels/')
        assert re.search(
            'Невозможно удалить метку, потому что она используется',
            self.page.text_content('.alert'),
        )
