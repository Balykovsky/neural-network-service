import time
import pika
from pika.exceptions import ConnectionClosed
from abc import ABCMeta, abstractmethod


class BaseConsumer(metaclass=ABCMeta):

    def __init__(self, host, port, virtual_host, username, password,
                 queue, reconnect_timeout=10, consuming_timeout=None):
        self._reconnect_timeout = reconnect_timeout
        self._consuming_timeout = consuming_timeout
        self._queue_name = queue
        self._connection_params = pika.ConnectionParameters(
            host=host, port=port, virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password))

    def _connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(self._connection_params)
                self._channel = self.connection.channel()
                self._channel.basic_qos(prefetch_count=1)
                self._init_callback()
                break
            except ConnectionClosed:
                time.sleep(self._reconnect_timeout)

    def _close(self):
        self.connection.close()

    def _reconnect(self):
        self._close()
        self._connect()

    def _init_callback(self):
        self._channel.basic_consume(self.callback, queue=self._queue_name)

    @abstractmethod
    def callback(self, ch, method, properties, body):
        pass

    def _consuming(self):
        try:
            if self._consuming_timeout:
                self.connection.add_timeout(self._consuming_timeout, self._channel.stop_consuming)
            self._channel.start_consuming()
        except ConnectionClosed:
            self._reconnect()

    def run(self):
        self._connect()
        try:
            while True:
                self._consuming()
                break
        finally:
            self._close()