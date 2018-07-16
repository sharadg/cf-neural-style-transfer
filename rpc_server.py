import pika
import sys
import math
from parse_cfenv import rabbit_env

connection_params = pika.URLParameters(rabbit_env)
connection = pika.BlockingConnection(connection_params)

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

PHI = (1+math.sqrt(5))/2


def binet_fib(n):
    return round((math.pow(PHI, n) - math.pow(-PHI, -n))/(2*PHI - 1))


def fib(n):
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, properties, body):
    n = int(body)
    print(" [.] fib({})".format(n))
    response = binet_fib(n)

    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=properties.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request,
                          queue='rpc_queue')
    print(' [*] Awaiting RPC requests. To exit press CTRL+C')
    channel.start_consuming()
