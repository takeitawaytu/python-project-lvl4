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
        cls.browser = cls.playwright.chromium.launch(timeout=3000)
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

    def login(self):
        """Login."""
        data = self.data['first']['user']
        self.page.goto(self.get_absolute_url('/login/'))
        self.page.wait_for_load_state()

        self.page.fill('input[name="username"]', data['username'])
        self.page.fill('input[name="password"]', data['password'])
        self.page.click('text="Войти"')
        self.page.wait_for_load_state()

    def test_index_no_auth(self):
        """Test cannot view if user no auth."""
        self.page.goto(self.get_absolute_url('/'))
        assert self.page.query_selector('text="Задачи"') is None

        self.page.goto(self.get_absolute_url('/tasks/'))
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

    def test_index(self):
        """Test index."""
        self.login()

        assert self.page.query_selector('text="Задачи"') is not None

        self.page.click('text="Задачи"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/tasks/')
        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )

        assert self.page.query_selector(row1) is not None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector(row3) is not None
        assert self.page.query_selector('text="Создать задачу"') is not None

        assert self.page.get_attribute('#id_status', 'value') is None
        assert self.page.get_attribute('#id_executor', 'value') is None
        assert self.page.get_attribute('#id_label', 'value') is None
        assert self.page.get_attribute('#id_self_tasks', 'value') is None
        assert self.page.query_selector('text="Показать"') is not None

    def test_create_task(self):
        """Test create task."""
        self.page.goto(self.get_absolute_url('/tasks/create/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

        self.login()

        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.click('text="Создать задачу"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/tasks/create/')
        assert self.page.get_attribute('#id_name', 'value') is None
        assert not self.page.text_content('#id_description')
        assert not self.page.select_option('#id_status')
        assert not self.page.select_option('#id_executor')
        assert not self.page.select_option('#id_labels')
        assert self.page.query_selector('text="Создать"') is not None

        task_data = self.data['five']['task']
        self.page.fill('input[name="name"]', task_data['name'])
        self.page.fill('textarea[name="description"]', task_data['description'])
        self.page.select_option(
            'select[name="status"]',
            label=task_data['status'],
        )
        self.page.select_option(
            'select[name="executor"]',
            label=task_data['executor'],
        )
        self.page.select_option(
            'select[name="labels"]',
            label=task_data['labels'],
        )
        self.page.click('text="Создать"')
        self.page.wait_for_load_state()
        assert self.page.url == self.get_absolute_url('/tasks/')
        assert re.search(
            'Задача успешно создана',
            self.page.text_content('.alert'),
        )
        row_created = '*css=tr >> text={text}'.format(text=task_data['status'])
        assert self.page.query_selector(row_created) is not None

    def test_update(self):
        """Test update."""
        self.page.goto(self.get_absolute_url('/tasks/42/update/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

        self.login()

        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()

        row_task = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row = self.page.query_selector(row_task)
        assert row is not None
        row.query_selector('text="Изменить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/tasks/\d+/update/', self.page.url)
        assert self.page.get_attribute('#id_name', 'value') == \
               self.data['first']['task']['name']
        assert self.page.text_content('#id_description') == \
               self.data['first']['task']['description']

        data_upd = self.data['five']['task']
        self.page.fill('input[name="name"]', data_upd['name'])
        self.page.fill('textarea[name="description"]', data_upd['description'])
        self.page.select_option('select[name="status"]', label=data_upd['status'])
        self.page.select_option('select[name="executor"]', label=data_upd['executor'])
        self.page.select_option('select[name="labels"]', label=data_upd['labels'])
        self.page.click('text="Изменить"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/tasks/')
        assert re.search(
            'Задача успешно изменена',
            self.page.text_content('.alert'),
        )

        row_upd = '*css=tr >> text={text}'.format(text=data_upd['name'])
        assert self.page.query_selector(row_upd) is not None

    def test_delete(self):
        """Test delete."""
        self.page.goto(self.get_absolute_url('/tasks/2/delete/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/login/')
        assert re.search(
            'Вы не авторизованы! Пожалуйста, выполните вход.',
            self.page.text_content('.alert'),
        )

        self.login()

        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()

        row_task = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row = self.page.query_selector(row_task)
        assert row is not None
        row.query_selector('text="Удалить"').click()
        self.page.wait_for_load_state()

        assert re.search(r'/tasks/\d+/delete/', self.page.url)
        self.page.click('text="Да, удалить"')
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/tasks/')
        assert re.search(
            'Задача успешно удалена',
            self.page.text_content('.alert'),
        )
        row_task = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        assert self.page.query_selector(row_task) is None

    def test_filter(self):
        """Test filter."""
        self.login()

        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()

        assert self.page.url == self.get_absolute_url('/tasks/')
        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )
        assert self.page.query_selector(row1) is not None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector(row3) is not None
        assert self.page.url == self.get_absolute_url('/tasks/')

        # by_author
        self.page.check('input[name="self_tasks"]')
        self.page.click('text="Показать"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )
        assert self.page.query_selector(row1) is not None
        assert self.page.query_selector(row2) is None
        assert self.page.query_selector(row3) is not None

        # by_status
        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()
        self.page.select_option(
            'select[name="status"]',
            label=self.data['second']['status']['name'],
        )
        self.page.click('text="Показать"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )
        assert self.page.query_selector(row1) is None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector(row3) is None

        # by_executor
        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()
        self.page.select_option(
            'select[name="executor"]',
            label=self.data['third']['user']['full_name'],
        )
        self.page.click('text="Показать"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )
        assert self.page.query_selector(row1) is None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector(row3) is not None

        # by_labels
        self.page.goto(self.get_absolute_url('/tasks/'))
        self.page.wait_for_load_state()
        self.page.select_option(
            'select[name="label"]',
            label=self.data['first']['labels']['name'],
        )
        self.page.click('text="Показать"')
        self.page.wait_for_load_state()

        row1 = '*css=tr >> text={text}'.format(
            text=self.data['first']['task']['name'],
        )
        row2 = '*css=tr >> text={text}'.format(
            text=self.data['second']['task']['name'],
        )
        row3 = '*css=tr >> text={text}'.format(
            text=self.data['third']['task']['name'],
        )
        assert self.page.query_selector(row1) is not None
        assert self.page.query_selector(row2) is not None
        assert self.page.query_selector(row3) is None

        # not_found_tasks
        self.page.select_option(
            'select[name="executor"]',
            label=self.data['fourth']['user']['full_name'],
        )
        self.page.click('text="Показать"')
        self.page.wait_for_load_state()
        row_task = '*css=tr >> text={text}'.format(text='Задачи не найдены')
        assert self.page.query_selector(row_task) is not None
