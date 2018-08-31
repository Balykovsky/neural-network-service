import threading
import json
from rest_framework.views import APIView
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from .tasks import neural_network_task
from .serializers import NeuralInputSerializer
from .models import NeuralNetwork, Task
from huey.contrib.djhuey import HUEY
from utils.base_producer import BaseProducer


class TaskManage(APIView):
    def get_object(self, taskid):
        try:
            task_obj = Task.objects.get(huey_id=taskid)
            return task_obj
        except:
            raise Http404

    def get(self, request, taskid):
        task = self.get_object(taskid)
        return Response(task.status)

    def post(self, request, taskid):
        task = self.get_object(taskid)
        try:
            producer = BaseProducer(host='localhost',
                                    port=5672,
                                    virtual_host='nnhost',
                                    username='nn',
                                    password='nnpass',
                                    queue=task.huey_id + '_stop',
                                    exchange='')
            producer.publish(body='stop')
            return Response('Success')
        except:
            return Response('Error')


class TaskStart(APIView):

    def post(self, request):
        serializer = NeuralInputSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data['name']
            path_list = serializer.data['path_list']
            # network = NeuralNetwork.objects.get(name=name)
            new_task = Task.objects.create()
            network_task = neural_network_task(tm=10)
            new_task.huey_id = network_task.task.task_id
            new_task.save()
            listen_tr = threading.Thread(target=listen_task, args=[HUEY, new_task.huey_id])
            listen_tr.start()
            return JsonResponse({'task_id': new_task.huey_id})

    def override_config(self):
        pass


def listen_task(huey_instance, current_task):
    listener = huey_instance.storage.listener()
    for message in listener.listen():
        print(message)
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if data['id'] == current_task:
                task = Task.objects.get(huey_id=current_task)
                task.status = data['status']
                task.save()
                if data['status'] == 'error-task':
                    if 'assert not lock.locked()' in data['traceback']:
                        task.status = 'stopped'
                        task.save()
                        try:
                            threading.current_thread()._stop()
                        except:
                            pass
                    task.status = data['status']
                    task.error = True
                    task.traceback = data['traceback']
                    task.save()
                if data['status'] == 'finished':
                    print('finished')
                    try:
                        threading.current_thread()._stop()
                    except:
                        pass
