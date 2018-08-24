import pika
import time
from pika.exceptions import ConnectionClosed


class BaseProducer:

    def __init__(self, host, port, virtual_host, username, password,
                 queue, exchange, reconnect_timeout=10):
        self._exchange = exchange
        self._queue_name = queue
        self._reconnect_timeout = reconnect_timeout
        self._connection_params = pika.ConnectionParameters(
            host=host, port=port, virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username=username,
                                              password=password))
        self.connection = None

    def _connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(self._connection_params)
                self._channel = self.connection.channel()
                self._channel.confirm_delivery()
                self._channel.queue_declare(queue=self._queue_name, auto_delete=True)
                break
            except ConnectionClosed:
                time.sleep(self._reconnect_timeout)

    def _close(self):
        self.connection.close()

    def _reconnect(self):
        self._close()
        self._connect()

    def publish(self, body):
        self._connect()
        try:
            while True:
                try:
                    result = self._channel.basic_publish(
                        exchange=self._exchange,
                        routing_key=self._queue_name,
                        body=body,
                        properties=pika.BasicProperties(delivery_mode=2),
                        mandatory=True,
                    )
                    return result
                except ConnectionClosed:
                    self._reconnect()
        finally:
            self._close()