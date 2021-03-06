# Generated by Django 3.2.9 on 2021-12-21 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('statuses', '0002_alter_status_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(error_messages={'blank': 'ThisFieldCannotBeBlank', 'unique': 'TaskWithThisNameAlreadyExist'}, help_text='HelpTaskFieldText', max_length=150, unique=True, verbose_name='TasksName')),
                ('description', models.TextField(blank=True, verbose_name='TaskDescription')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='creators', to=settings.AUTH_USER_MODEL, verbose_name='TaskCreator')),
                ('executor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='executors', to=settings.AUTH_USER_MODEL, verbose_name='TaskExecutor')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='statuses', to='statuses.status', verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['-created_at'],
            },
        ),
    ]
