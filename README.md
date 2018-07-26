# Python code for neural style transfer application

This repo contains 2 different modules.
1. Flask web app that exposes a frontend app and a REST API for invoking commands and uploading content files to transform

2. Backend Python apps running TensorFlow code for doing the image transformations and a Fibonacci generator for confirming that the setup is working fine

## Dependencies
 - Helm install of RabbitMQ to act the glue layer between REST API and backend services
 - Connectivity between K8s runtime and docker registry that has the images for running the application
 - Access to GPUs to get practical results in few secods
 - Pre-trained model downloaded and saved in images folder [Imagenet-VGG-19](http://www.vlfeat.org/matconvnet/models/imagenet-vgg-verydeep-19.mat)

## Runtime Support
- ### For running locally (natively on macos)
```
1. Start RabbitMQ Server
- brew services run rabbitmq

2. Set ENV profile to local
- export profile=local

3. Start main Flask REST API server
- python app.py                                                                                                                                                                                                                                                        ✹ ✭
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

4. In a separate terminal window (export the profile variable and then, run the following for fibonacci RPC server)
- python rpc_server.py                                                                                                                                                                                                                                                 ✹ ✭
 [*] Awaiting RPC requests. To exit press CTRL+C

5. In a separate terminal window (export the profile variable and then, run the following for main TensorFlow serving layer)
- python neural_style_server.py                                                                                                                                                                                                                                      ⏎ ✹ ✭
 [*] Awaiting TensorFlow RPC requests. To exit press CTRL+C

6. Test Fibonacci Server
- http -v :5000/fib/45                                                                                                                                                                                                                                               ⏎ ✹ ✭
GET /fib/45 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:5000
User-Agent: HTTPie/0.9.9

HTTP/1.0 200 OK
Content-Length: 11
Content-Type: application/json
Date: Thu, 26 Jul 2018 01:51:12 GMT
Server: Werkzeug/0.14.1 Python/3.6.6

1134903170

7. Test Image Transformation
- http -fF --timeout=600 :5000/transform/ filename@~/Downloads/taj-mahal.jpg num_iterations==2 raw==1 > /tmp/taj-mahal-transformed.jpg
- open /tmp/taj-mahal-transformed.jpg
```
- ### For running on k8s cluster (see the yaml files for creating resources)
  - [Flask Web Server - for REST apis](flask-web.yml)
  - [Flask Fibonnaci Server - for serving fibonnaci numbers](flask-fib.yml)

## TODO
 1. References
