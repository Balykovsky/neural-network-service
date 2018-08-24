import time
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from .tasks import base_task, test_task
from .celery import app
from celery.result import AsyncResult
from .serializers import NeuralInputSerializer
from .models import NeuralNetwork, Task


class TaskManage(APIView):
    def get_object(self, pk):
        try:
            task_obj = Task.objects.get(pk=pk)
            return AsyncResult(task_obj.celery_id, app=app)
        except:
            raise Http404

    def get(self, request, pk):
        task = self.get_object(pk)
        return Response(task.state)

    def post(self, request, pk):
        task = self.get_object(pk)
        try:
            task.revoke(terminate=True)
            return Response('Success')
        except:
            return Response('Error')


class TaskStart(APIView):

    def get(self, request):
        a = test_task.delay()
        print(a)
        print(dir(a))
        return Response()

    def post(self, request):
        serializer = NeuralInputSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data['name']
            path_list = serializer.data['path_list']
            # network = NeuralNetwork.objects.get(name=name)
            new_task = Task.objects.create()
            network_task = test_task.delay(30, new_task.id)
            new_task.celery_id = network_task.task_id
            return Response(new_task.id)

    def override_config(self):
        pass
