# Generated by Django 2.1 on 2018-08-29 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_network_service', '0003_auto_20180824_1227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='celery_id',
            new_name='huey_id',
        ),
        migrations.AddField(
            model_name='task',
            name='error',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(default='Ready to start', max_length=100),
        ),
        migrations.AddField(
            model_name='task',
            name='traceback',
            field=models.TextField(blank=True, null=True),
        ),
    ]
