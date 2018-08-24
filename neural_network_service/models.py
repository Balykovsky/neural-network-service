from django.db import models


class NeuralNetwork(models.Model):
    name = models.CharField(max_length=100)
    path_to_config = models.CharField(max_length=1000)


class Task(models.Model):
    celery_id = models.CharField(blank=True, null=True, max_length=100)
