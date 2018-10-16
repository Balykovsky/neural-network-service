import threading
import json
import os
from functools import partial
from datetime import timedelta
from django.utils import timezone
from neural_network_service.settings import BASE_DIR
from utils.base_producer import BaseProducer
from utils.base_consumer import BaseConsumer
from utils.exceptions import NeuralNetworkStopExceptions
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, HUEY
from neural_network_service.test_predictor import TestPredictor
from neural_network_service.models import Task
from utils.assets import delete_task_data


class TerminateConsumer(BaseConsumer):
    def callback(self, ch, method, properties, body):
        self.event.set()
        self._shutdown()
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            pass


class TerminateListenThread(TerminateConsumer, threading.Thread):
    def __init__(self, event, *args, **kwargs):
        self.event = event
        super(TerminateConsumer, self).__init__(*args, **kwargs)
        threading.Thread.__init__(self)


class NeuralNetworkResultProcessing:
    def __init__(self):
        self._count = 0

    def callback(self, target, producer, stop_event, path_qty, path_list, task):
        if stop_event.is_set():
            raise NeuralNetworkStopExceptions('Neural network stopped by client')
        start_qty = path_qty - len(path_list)
        progress = int((start_qty + self._count) * 100 / path_qty)
        result = {'path': path_list[self._count], 'target': target}
        msg = {'result': result,
               'status': 'In progress {}%'.format(progress),
               'extra': {}}
        producer.publish(body=json.dumps(msg))
        self._store_result(result, task)
        if progress % 5 == 0:
            HUEY.emit_task(status='in progress', task=task, progress=progress)
        self._count += 1

    def _store_result(self, result, task):
        head, tail = os.path.split(result['path'])
        file_name = 'predict_{}.json'.format(tail.split('.')[0])
        task_path = os.path.join(BASE_DIR, 'results', task.task_id)
        if not os.path.exists(task_path):
            os.makedirs(task_path)
        path = os.path.join(task_path, file_name)
        with open(path, 'w') as outfile:
            json.dump(result, outfile)

    def join_results(self):
        # join results in single json
        pass

@task(include_task=True)
def neural_network_task(path_list, path_qty, task=None):
    stop_event = threading.Event()
    listener = TerminateListenThread(host=os.getenv('RABBITMQ_HOST'),
                                     port=os.getenv('RABBITMQ_PORT'),
                                     virtual_host=os.getenv('RABBITMQ_DEFAULT_VHOST'),
                                     username=os.getenv('RABBITMQ_DEFAULT_USER'),
                                     password=os.getenv('RABBITMQ_DEFAULT_PASS'),
                                     queue=task.task_id + '_stop',
                                     consuming_timeout=None,
                                     event=stop_event)
    listener.start()
    producer = BaseProducer(host=os.getenv('RABBITMQ_HOST'),
                            port=os.getenv('RABBITMQ_PORT'),
                            virtual_host=os.getenv('RABBITMQ_DEFAULT_VHOST'),
                            username=os.getenv('RABBITMQ_DEFAULT_USER'),
                            password=os.getenv('RABBITMQ_DEFAULT_PASS'),
                            queue=task.task_id,
                            exchange='')
    try:
        msg = {'result': None,
               'status': None,
               'extra': {}}
        predictor = TestPredictor(path_list=path_list)
        res_process = NeuralNetworkResultProcessing()
        modify_callback = partial(res_process.callback,
                                  producer=producer,
                                  stop_event=stop_event,
                                  path_qty=path_qty,
                                  path_list=path_list,
                                  task=task)
        predictor.predict(modify_callback)
    except NeuralNetworkStopExceptions:
        msg['result'] = None
        msg['status'] = 'Stopped'
        msg['extra'].update(last_num=res_process._count)
        producer.publish(body=json.dumps(msg))
        raise
    except:
        msg['result'] = None
        msg['status'] = 'Error'
        msg['extra'].update(last_num=res_process._count)
        producer.publish(body=json.dumps(msg))
        listener._shutdown()
        raise
    else:
        msg['result'] = None
        msg['status'] = 'Finished'
        msg['extra'] = {}
        # res_process.join_results()
        listener._shutdown()
        producer.publish(body=json.dumps(msg))


@periodic_task(crontab(minute='3', hour='14'))
def delete_expired_results():
    expired_tasks = Task.objects.filter(finished_at__lte=timezone.now()-timedelta(days=5))
    for task in expired_tasks:
        delete_task_data(task)
