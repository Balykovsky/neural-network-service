import requests
import json
from threading import Thread

from utils.base_consumer import BaseConsumer


class NeuralNetworkTask:
    def __init__(self):
        self.base_url = ''
        self.id = None
        self.listener = None
        self.data = None
        self.cont = False

    def start(self, name, path_list, extra):
        if self.id and not self.cont:
            return 'Network already started on this instance'
        self.data = {'name': name,
                     'path_list': path_list,
                     'extra': extra
                     }
        self.cont = False
        try:
            response = requests.post(url=self.base_url,
                                     json=self.data,
                                     headers={'content-type': 'application/json'})
        except:
            return 'Server is not available now'
        else:
            if response.status_code == 200:
                self.id = response.json()['task_id']
                listener = NetworkListenThread(host='',
                                               port=5672,
                                               virtual_host='nnhost',
                                               username='nn',
                                               password='nnpass',
                                               queue=self.id,
                                               consuming_timeout=None)
                listener.start()
                self.listener = listener
                return 'Network started, id: {}'.format(self.id)
            elif response.status_code == 400:
                return 'Invalid data provided'
            elif response.status_code == 404:
                return 'Server is not available now'

    def stop(self, reject=False):
        if not self.id:
            return 'Network not started on this instance yet'
        url = self.base_url + self.id + '/'
        response = requests.post(url=url,
                                 json={'reject': reject},
                                 headers={'content-type': 'application/json'})
        if response.status_code == 200:
            self.cont = True
            if reject:
                self.cont = False
                # delete data
        return response.status_code, response.text

    def get_state(self):
        if not self.id:
            return 'Network not started on this instance yet'
        url = self.base_url + self.id + '/'
        response = requests.get(url=url)
        return response.status_code, response.text

    def continue_stopped(self):
        if self.listener.last_num and self.data and self.data['path_list']:
            self.data['path_list'] = self.data['path_list'][int(self.listener.last_num):]
            self.data['extra'].update(rerun='true', id=self.id)
            if self.listener.error:
                self.cont = True
            self.start(**self.data)


class NetworkConsumer(BaseConsumer):
    def callback(self, ch, method, properties, body):
        msg = json.loads(body)
        print(msg)
        if msg['extra'] and 'last_num' in msg['extra'].keys():
            self.last_num = msg['extra']['last_num']
        ch.basic_ack(delivery_tag=method.delivery_tag)
        if msg['status'] in ['Finished', 'Error', 'Stopped']:
            if msg['status'] == 'Error':
                self.error = True
            self._shutdown()


class NetworkListenThread(NetworkConsumer, Thread):
    def __init__(self, *args, **kwargs):
        super(NetworkConsumer, self).__init__(*args, **kwargs)
        Thread.__init__(self)
        self.last_num = None
        self.error = False
