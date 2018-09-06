import time
import threading
import json
from utils.base_producer import BaseProducer
from utils.base_consumer import BaseConsumer
from utils.exceptions import NeuralNetworkStopExceptions
from huey.contrib.djhuey import task
# from some import neuro1, neuro2, neuro3, neuro4


# NEURAL_NETWORKS = {
#     'neuro1': neuro1,
#     'neuro2': neuro2,
#     'neuro3': neuro3,
#     'neuro4': neuro4
# }

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


@task(include_task=True)
def neural_network_task(path_list, path_qty, task=None):
    stop_event = threading.Event()
    listener = TerminateListenThread(host='localhost',
                                     port=5672,
                                     virtual_host='nnhost',
                                     username='nn',
                                     password='nnpass',
                                     queue=task.task_id + '_stop',
                                     consuming_timeout=None,
                                     event=stop_event)
    listener.start()
    producer = BaseProducer(host='localhost',
                            port=5672,
                            virtual_host='nnhost',
                            username='nn',
                            password='nnpass',
                            queue=task.task_id,
                            exchange='')
    try:
        count = 0
        start_qty = path_qty - len(path_list)
        for i in path_list:
            msg = {'result': str(i),
                   'status': 'In progress {}%'.format(int((start_qty+count)*100/path_qty)),
                   'extra': {}}
            if stop_event.is_set():
                raise NeuralNetworkStopExceptions('Neural network stopped by client')
            producer.publish(body=json.dumps(msg))
            # if count == 15:
            #     k = count/0
            count += 1
            time.sleep(1)
    except NeuralNetworkStopExceptions:
        msg['result'] = None
        msg['status'] = 'Stopped'
        msg['extra'].update(last_num=count)
        producer.publish(body=json.dumps(msg))
        raise
    except:
        msg['result'] = None
        msg['status'] = 'Error'
        msg['extra'].update(last_num=count)
        producer.publish(body=json.dumps(msg))
        listener._shutdown()
        raise
    else:
        msg['result'] = None
        msg['status'] = 'Finished'
        msg['extra'] = {}
        listener._shutdown()
        producer.publish(body=json.dumps(msg))