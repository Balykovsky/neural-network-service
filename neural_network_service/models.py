from django.db import models


class NeuralNetwork(models.Model):
    name = models.CharField(max_length=100)
    path_to_config = models.CharField(max_length=1000)


class Task(models.Model):
    huey_id = models.CharField(blank=True, null=True, max_length=100)
    status = models.CharField(default='Ready to start', max_length=100)
    error = models.BooleanField(default=False)
    traceback = models.TextField(blank=True, null=True)

#
# class Listener(models.Model):
#     is_active = models.BooleanField(default=False)
