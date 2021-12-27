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

    def test_index(self):
        """Test index page users."""
        self.page.goto(self.get_absolute_url('/'))

        assert self.page.query_selector('text="Вход"') is not None
        assert self.page.query_selector('text="Регистрация"') is not None
        assert self.page.query_selector('text="Выход"') is None

        self.page.click('text="Пользователи"')
        self.page.wait_for_load_state()
        row_user1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['user']['full_name'],
        )
        row_user2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['user']['full_name'],
        )
        row_user3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['user']['full_name'],
        )

        assert self.page.query_selector(row_user1) is not None
        assert self.page.query_selector(row_user2) is None
        assert self.page.query_selector(row_user3) is not None

        self.login(self.data['first']['user'])
        assert self.page.query_selector('text="Вход"') is None
        assert self.page.query_selector('text="Регистрация"') is None
        assert self.page.query_selector('text="Выход"') is not None

    def test_create(self):
        """Test create."""
        data = self.data['second']['user']
        self.page.goto(self.get_absolute_url('/users/create/'))

        assert self.page.get_attribute('#id_first_name', 'value') is None
        assert self.page.get_attribute('#id_last_name', 'value') is None
        assert self.page.get_attribute('#id_username', 'value') is None
        assert self.page.get_attribute('#id_password1', 'value') is None
        assert self.page.get_attribute('#id_password2', 'value') is None

        self.page.fill('input[name="first_name"]', data['first_name'])
        self.page.fill('input[name="last_name"]', data['last_name'])
        self.page.fill('input[name="username"]', data['username'])
        self.page.fill('input[name="password1"]', data['password'])
        self.page.fill('input[name="password2"]', data['password'])
        self.page.click('text=Зарегистрировать')
        self.page.wait_for_load_state()
        assert re.search(
            'Пользователь успешно зарегистрирован',
            self.page.text_content('.alert'),
        )
        assert self.page.url == self.get_absolute_url('/login/')

    def test_sign_in_sign_out(self):
        """Test login/logout user."""
        user_data = self.data['first']['user']
        self.page.goto(self.get_absolute_url('/'))
        assert self.page.query_selector('text="Вход"') is not None
        assert self.page.query_selector('text="Регистрация"') is not None

        assert self.page.query_selector('text="Выход"') is None

        self.page.click('text="Вход"')
        self.page.wait_for_load_state()

        self.page.fill('input[name="username"]', user_data['username'])
        self.page.fill('input[name="password"]', user_data['password'])
        self.page.click('text="Войти"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/')
        assert re.search('Вы залогинены', self.page.text_content('.alert'))

        self.page.click('text="Выход"')
        self.page.wait_for_load_state()
        assert self.page.url == self.get_absolute_url('/')
        assert re.search('Вы разлогинены', self.page.text_content('.alert'))

    def test_update(self):
        """Test update."""
        data = self.data['first']['user']
        self.login(data)

        self.page.click('text="Пользователи"')
        self.page.wait_for_load_state()

        row_user1 = '*css=tr >> text={text}'.format(text=data['full_name'])
        row = self.page.query_selector(row_user1)
        assert row is not None
        row.query_selector('text="Изменить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/users/\d+/update/', self.page.url)
        assert self.page.get_attribute('#id_first_name', 'value') == data['first_name']
        assert self.page.get_attribute('#id_last_name', 'value') == data['last_name']
        assert self.page.get_attribute('#id_username', 'value') == data['username']
        assert self.page.get_attribute('#id_password1', 'value') is None
        assert self.page.get_attribute('#id_password2', 'value') is None

        data_upd = self.data['second']['user']
        self.page.fill('input[name="first_name"]', data_upd['first_name'])
        self.page.fill('input[name="last_name"]', data_upd['last_name'])
        self.page.fill('input[name="username"]', data_upd['username'])
        self.page.fill('input[name="password1"]', data_upd['password'])
        self.page.fill('input[name="password2"]', data_upd['password'])

        self.page.click('text="Изменить"')
        self.page.wait_for_load_state()
        assert self.page.url == self.get_absolute_url('/users/')
        assert re.search(
            'Пользователь успешно изменён',
            self.page.text_content('.alert'),
        )

        row_user2 = '*css=tr >> text={text}'.format(text=data_upd['full_name'])
        assert self.page.query_selector(row_user2) is not None

    def test_cannot_update_no_auth(self):
        """Test cannot update if user no auth"""
        self.page.goto(self.get_absolute_url('/users/'))
        self.page.wait_for_load_state()

        row_user1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['user']['full_name'],
        )
        assert self.page.query_selector(row_user1) is not None
        row = self.page.query_selector(row_user1)
        assert row is not None
        row.query_selector('text="Изменить"').click()
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

    def test_delete(self):
        """Test delete."""
        data = self.data['fourth']['user']
        self.login(data)

        self.page.click('text="Пользователи"')
        self.page.wait_for_load_state()

        row_user = '*css=tr >> text={text}'.format(text=data['full_name'])
        row = self.page.query_selector(row_user)
        assert row is not None
        row.query_selector('text="Удалить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/users/\d+/delete/', self.page.url)
        self.page.click('text="Да, удалить"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/users/')
        assert re.search(
            'Пользователь успешно удалён',
            self.page.text_content('.alert'),
        )

    def test_cannot_delete_no_auth(self):
        """Test cannot delete if user no auth"""
        self.page.goto(self.get_absolute_url('/users/'))
        self.page.wait_for_load_state()

        row_user1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['user']['full_name'],
        )
        assert self.page.query_selector(row_user1) is not None
        row = self.page.query_selector(row_user1)
        assert row is not None
        row.query_selector('text="Удалить"').click()
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )
