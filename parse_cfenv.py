import os
import urllib
from cfenv import AppEnv


rabbit_env = ""

if os.getenv("profile", "cloud") == "local":
    # Running in a local or dev environment
    rabbit_env = "amqp://{}:{}@{}:{}/{}?heartbeat_interval=30".format(
        os.getenv("rabbitmq.username", "guest"),
        os.getenv("rabbitmq.password", "guest"),
        os.getenv("rabbitmq.server", "localhost"),
        os.getenv("rabbitmq.port", "5672"),
        urllib.parse.quote_plus(os.getenv("rabbitmq.vhost", "/")),
    )
else:
    cfenv = AppEnv()
    rabbit_env = cfenv.get_service(label="p-rabbitmq").get_url("uri")
    rabbit_env = rabbit_env + "?heartbeat_interval=30"

if __name__ == "main":
    cfenv.name  # 'test-app'
    cfenv.port  # 5000

    # rabbitmq = cfenv.get_service(label='rabbitmq')
    # rabbitmq.credentials  # {'uri': '...', 'password': '...'}
    # rabbitmq.get_url(host='hostname', password='password', port='port')  # redis://pass:host
