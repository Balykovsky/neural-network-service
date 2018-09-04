from django.db import models


class NeuralNetwork(models.Model):
    name = models.CharField(max_length=100)
    path_to_config = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Task(models.Model):
    huey_id = models.CharField(blank=True, null=True, max_length=50)
    status = models.CharField(default='Ready to start', max_length=20)
    error = models.BooleanField(default=False)
    traceback = models.TextField(blank=True, null=True)
    path_qty = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.huey_id
