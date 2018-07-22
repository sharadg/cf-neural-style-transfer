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
- ### For running locally (natively on macos or ubuntu)
- ### For running on k8s cluster (see the yaml files for creating resources)
  - [Flask Web Server - for REST apis](flask-web.yml)
  - [Flask Fibonnaci Server - for serving fibonnaci numbers](flask-fib.yml)

## TODO
 1. References
