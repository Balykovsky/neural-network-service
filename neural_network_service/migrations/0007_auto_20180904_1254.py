# Generated by Django 2.1 on 2018-09-04 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_network_service', '0006_auto_20180904_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='huey_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(default='Ready to start', max_length=20),
        ),
    ]
