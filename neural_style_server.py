import base64
import io
import json
import pika
import threading
import logging
# from neural_style import NeuralStyleTransfer
from parse_cfenv import rabbit_env
from tfadain.test import style_transfer

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# neural_style_transfer = NeuralStyleTransfer()


class NeuralStyleRPCServer(object):
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
            self._channel.queue_declare(queue="tf_rpc_queue")
            self._channel.basic_consume(self.on_request, queue="tf_rpc_queue")
            self._channel.start_consuming()

    def on_request(self, ch, method, properties, body):
        if (
                properties.content_type is not None
                and properties.content_type == "application/json"
        ):
            req = json.loads(body) if type(body) == type("str") else json.loads(body.decode())
            print(" [.] Received request to process file: " + req["filename"])
            logger.info('received request message with correlation id: %s', properties.correlation_id)
        else:
            req = body

        # do the neural style on req.content image object by doing reverse of base64.b64encode(file.read()).decode()
        image_format = (
            str(req["content_type"]).rsplit("/")[1]
            if req["content_type"] is not None
            else "jpg"
        )

        raw_img_bytes = base64.b64decode(req["content"].encode())
        num_iterations = int(req["num_iterations"]
                             ) if req["num_iterations"] else 20
        alpha = float(req["alpha"])
        gpu = int(req["gpu"])

        content_image = io.BytesIO(raw_img_bytes)
        content_image.name = req["filename"]
        style_image = "tfadain/input/style/" + req["style"] + ".jpg"

        # spawn another thread for processing the file
        # stylized_image_arr = neural_style_transfer.model_nn(content_image, style_image, num_iterations)
        stylized_image_arr = []
        processing_thread = threading.Thread(target=process_message,
                                             args=(content_image, style_image, stylized_image_arr, alpha, gpu))
        processing_thread.start()
        while processing_thread.is_alive():
            processing_thread.join(timeout=5.0)
            self._connection.process_data_events()

        stylized_image = stylized_image_arr.pop()

        msg = {
            "filename": req["filename"] + "_stylized_" + req["style"],
            "content": base64.b64encode(stylized_image.read()).decode(),
        }
        response = json.dumps(msg)

        logger.info(" [x] Sending Response: %s ", req["filename"])

        try:
            self.publish(response, properties.content_type,
                         properties.correlation_id, properties.reply_to, method)

        except pika.exceptions.ConnectionClosed:
            # In case of sending a reply message, if the channel is closed then the message will be redelivered
            logger.info("Exception while sending response, reconnecting...")
            self.connect()
            self.publish(response, properties.content_type,
                         properties.correlation_id, properties.reply_to, method)

    def publish(self, msg, content_type, correlation_id, routing_key, method, exchange=''):
        self._channel.basic_publish(exchange=exchange,
                                    routing_key=routing_key,
                                    properties=pika.BasicProperties(
                                        content_type=content_type,
                                        correlation_id=correlation_id),
                                    body=str(msg))
        self._channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(
            'sending response message with correlation id: %s', correlation_id)


def process_message(content_image, style_image, stylized_image_arr, alpha, gpu):
    stylized_image_arr.append(
        style_transfer(content=content_image, content_size=600, style=style_image, style_size=600, alpha=alpha, gpu=gpu))


if __name__ == "__main__":
    print(" [*] Awaiting TensorFlow RPC requests. To exit press CTRL+C")
    neural_style_server = NeuralStyleRPCServer()
