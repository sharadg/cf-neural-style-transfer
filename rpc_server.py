import pika
import sys
import math
from parse_cfenv import rabbit_env

PHI = (1 + math.sqrt(5)) / 2


def binet_fib(n):
    return round((math.pow(PHI, n) - math.pow(-PHI, -n)) / (2 * PHI - 1))


class FibonacciRPCServer(object):
    def __init__(self):
        self._connection_params = pika.URLParameters(rabbit_env)
        self._connection = None
        self._channel = None
        self.connect()

    def connect(self):
        if not self._connection or self._connection.is_closed:
            self._connection = pika.BlockingConnection(self._connection_params)
            self._channel = self._connection.channel()
            self._channel.basic_qos(prefetch_count=1)
            self._channel.queue_declare(queue="rpc_queue")
            self._channel.basic_consume(self.on_request, queue="rpc_queue")
            self._channel.start_consuming()

    def on_request(self, ch, method, properties, body):
        n = int(body)
        print(" [.] Received request to fib({}): ".format(n))
        sys.stderr.write('received request message with correlation id: {}\n'.format(properties.correlation_id))
        response = binet_fib(n)

        try:
            self.publish(response, properties.correlation_id, properties.reply_to, method)

        except pika.exceptions.ConnectionClosed:
            # In case of sending a reply message, if the channel is closed then the message will be redelivered
            sys.stderr.write("Exception while sending response, reconnecting...\n")
            self.connect()
            self.publish(response, properties.correlation_id, properties.reply_to, method)

    def publish(self, msg, correlation_id, routing_key, method, exchange=''):
        self._channel.basic_publish(exchange=exchange,
                                    routing_key=routing_key,
                                    properties=pika.BasicProperties(
                                        correlation_id=correlation_id),
                                    body=str(msg))
        self._channel.basic_ack(delivery_tag=method.delivery_tag)
        sys.stderr.write('sending response message with correlation id: {}\n'.format(correlation_id))


if __name__ == "__main__":
    print(' [*] Awaiting RPC requests. To exit press CTRL+C')
    fibonacci_server = FibonacciRPCServer()
