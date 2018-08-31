import time, threading, _thread
from utils.base_producer import BaseProducer
from utils.base_consumer import BaseConsumer
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
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self._shutdown()
        try:
            threading.current_thread()._stop()
        except:
            pass


class TerminateListenThread(TerminateConsumer, threading.Thread):
    def __init__(self, event, *args, **kwargs):
        self.event = event
        super(TerminateConsumer, self).__init__(*args, **kwargs)
        threading.Thread.__init__(self)


def base_task(name, path_list, task_id):
    producer = BaseProducer(queue=str(task_id))
    # network = NEURAL_NETWORKS[name]
    # network(path_list, producer)
    # predict code
    # producer.publish(body='some predict result')

def test_task(tm, task_id):
    producer = BaseProducer(host='localhost',
                            port=5672,
                            virtual_host='nnhost',
                            username='nn',
                            password='nnpass',
                            queue='queue_{}'.format(task_id),
                            exchange='')
    for i in range(tm):
        time.sleep(1)
        producer.publish(body=str(i))
        if i == 29:
            return i


@task(include_task=True)
def neural_network_task(tm, task=None):
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
        for i in range(tm):
            if stop_event.is_set():
                threading.current_thread()._stop()
            producer.publish(body=str(i))
            # if i == 25:
            #     k = i/0
            time.sleep(1)
    except:
        producer.publish(body='Error')
        listener._shutdown()
        raise