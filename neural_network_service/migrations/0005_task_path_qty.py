# Generated by Django 2.1 on 2018-09-04 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_network_service', '0004_auto_20180829_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='path_qty',
            field=models.IntegerField(default=0),
        ),
    ]
