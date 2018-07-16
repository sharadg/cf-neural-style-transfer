import sys
import uuid
import time
import logging
import pika
from parse_cfenv import rabbit_env


class FibonacciRPCClient(object):
    def __init__(self):
        self._connection_params = pika.URLParameters(rabbit_env)
        self._connection = None
        self.connect()

    def connect(self):
        if not self._connection or self._connection.is_closed:
            self._connection = pika.BlockingConnection(self._connection_params)
            self._channel = self._connection.channel()
            result = self._channel.queue_declare(exclusive=True)
            self._callback_queue = result.method.queue
            self._channel.basic_consume(self.on_response, no_ack=True,
                                        queue=self._callback_queue)

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = body

    def _publish(self, msg, correlation_id, exchange='', routing_key='rpc_queue'):
        self._channel.basic_publish(exchange='',
                                    routing_key='rpc_queue',
                                    properties=pika.BasicProperties(
                                        reply_to=self._callback_queue,
                                        correlation_id=correlation_id),
                                    body=str(msg))
        logging.debug('message sent: {}'.format(msg))

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        try:
            self._publish(n, correlation_id=self.corr_id)
        except pika.exceptions.ConnectionClosed:
            logging.debug('Reconnectinng...')
            time.sleep(0.5)
            self.connect()
            self._publish(n, correlation_id=self.corr_id)

        while self.response is None:
            self._connection.process_data_events()
        return int(self.response)


if __name__ == "__main__":
    fibonacci_rpc = FibonacciRPCClient()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(' [*] Requesting fib({})'.format(n))
    response = fibonacci_rpc.call(n)
    print(' [.] Got {}'.format(response))
