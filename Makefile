.PHONY: shell lint test

install:
	poetry install

makemigrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

shell:
	poetry run python manage.py shell

start_server:
	poetry run python manage.py runserver 127.0.0.1:8000

requirements: poetry.lock
	poetry export --format requirements.txt --output requirements.txt

test:
	poetry run python manage.py test

test-coverage:
	poetry run coverage run --source='task_manager' manage.py test
	poetry run coverage xml
	poetry run coverage report

lint:
	poetry run flake8 task_manager --exclude=task_manager/settings.py

i18n_mm:
	poetry run django-admin makemessages -l ru
	poetry run django-admin makemessages -l en

i18n_compile
	poetry run django-admin.py compilemessages -l ru
	poetry run django-admin.py compilemessages -l en