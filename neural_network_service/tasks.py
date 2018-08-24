from celery import shared_task
import time
from utils.base_producer import BaseProducer
# from some import neuro1, neuro2, neuro3, neuro4


# NEURAL_NETWORKS = {
#     'neuro1': neuro1,
#     'neuro2': neuro2,
#     'neuro3': neuro3,
#     'neuro4': neuro4
# }

@shared_task
def base_task(name, path_list, task_id):
    producer = BaseProducer(queue=str(task_id))
    # network = NEURAL_NETWORKS[name]
    # network(path_list, producer)
    # predict code
    # producer.publish(body='some predict result')

@shared_task
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