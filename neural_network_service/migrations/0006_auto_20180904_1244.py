# Generated by Django 2.1 on 2018-09-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_network_service', '0005_task_path_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='finished_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='started_at',
            field=models.DateTimeField(null=True),
        ),
    ]