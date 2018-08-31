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
        self._shutdown()
        self.event.set()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            threading.current_thread()._stop()
        except:
            pass


class TerminateListenThread(TerminateConsumer, threading.Thread):
    def __init__(self, event, *args, **kwargs):
        self.event = event
        super(TerminateConsumer, self).__init__(*args, **kwargs)
        threading.Thread.__init__(self)


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
            # if i == 5:
            #     k = i/0
            time.sleep(1)
    except:
        producer.publish(body='Error')
        if listener.connection.is_open:
            listener._shutdown()
        raise
    else:
        if listener.connection.is_open:
            listener._shutdown()
        producer.publish(body='Finished')