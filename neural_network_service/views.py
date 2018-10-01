import threading
import json
import datetime
import os
from rest_framework import status
from rest_framework.views import APIView
from neural_network_service.settings import BASE_DIR
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from neural_network_service.tasks import neural_network_task
from neural_network_service.serializers import NeuralInputSerializer
from neural_network_service.models import NeuralNetwork, Task
from huey.contrib.djhuey import HUEY
from utils.base_producer import BaseProducer
from utils.assets import delete_task_data


class TaskManage(APIView):

    def get(self, request, taskid):
        task = get_object_or_404(Task, huey_id=taskid)
        return Response(task.status)

    def post(self, request, taskid):
        task = get_object_or_404(Task, huey_id=taskid)
        try:
            producer = BaseProducer(host=os.getenv('RABBITMQ_HOST'),
                                    port=os.getenv('RABBITMQ_PORT'),
                                    virtual_host=os.getenv('RABBITMQ_DEFAULT_VHOST'),
                                    username=os.getenv('RABBITMQ_DEFAULT_USER'),
                                    password=os.getenv('RABBITMQ_DEFAULT_PASS'),
                                    queue=task.huey_id + '_stop',
                                    exchange='')
            producer.publish(body='stop')
            if request.data['reject']:
                delete_task_data(task)
                return Response('Neural network task successfully suspended and rejected')
            return Response('Neural network task successfully suspended')
        except:
            return Response('Suspend is not available now', status=status.HTTP_404_NOT_FOUND)


class TaskStart(APIView):

    def post(self, request):
        serializer = NeuralInputSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data['name']
            path_list = serializer.data['path_list']
            extra_data = serializer.data['extra']
            if extra_data and ('rerun' in extra_data.keys()):
                new_task = get_object_or_404(huey_id=extra_data['id'])
                path_to_rename = os.path.join(BASE_DIR, 'results', new_task.huey_id)
            else:
                new_task = Task.objects.create(path_qty=len(path_list))
            # network = NeuralNetwork.objects.get(name=name)
            network_task = neural_network_task(path_list=path_list,
                                               path_qty=new_task.path_qty)
            if 'path_to_rename' in locals():
                os.rename(path_to_rename, os.path.join(BASE_DIR, 'results', network_task.task.task_id))
            new_task.huey_id = network_task.task.task_id
            new_task.save()
            listen_tr = threading.Thread(target=listen_task,
                                         args=[HUEY, new_task.huey_id])
            listen_tr.start()
            return JsonResponse({'task_id': new_task.huey_id})
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def override_config(self):
        pass


def listen_task(huey_instance, current_task):
    listener = huey_instance.storage.listener()
    for message in listener.listen():
        print(message)
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if data['status'] == 'checking-periodic':
                continue
            if data['id'] == current_task:
                task = get_object_or_404(Task, huey_id=current_task)
                task.status = data['status']
                task.save()
                if data['status'] == 'started' and not task.started_at:
                    task.started_at = timezone.now()
                elif data['status'] == 'error-task':
                    if 'Neural network stopped by client' in data['traceback']:
                        task.status = 'stopped'
                        task.save()
                        return
                    task.error = True
                    task.finished_at = timezone.now()
                    task.traceback = data['traceback']
                elif data['status'] == 'finished':
                    task.finished_at = timezone.now()
                elif data['status'] == 'in progress':
                    task.progress = data['progress']
                task.save()
                if task.status in ['error-task', 'finished', 'stopped']:
                    return
