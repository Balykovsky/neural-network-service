# Generated by Django 2.1 on 2018-09-11 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_network_service', '0007_auto_20180904_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='progress',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
