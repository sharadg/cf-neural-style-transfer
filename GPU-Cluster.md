# Create a GPU cluster

## Didn't work
gcloud beta container clusters create "gpu-cluster" --zone "us-central1-f" --username "admin" --cluster-version "1.10.5-gke.3" --machine-type "n1-standard-2" --accelerator "type=nvidia-tesla-v100,count=1" --image-type "UBUNTU" --disk-type "pd-standard" --disk-size "100" --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "2" --enable-cloud-logging --enable-cloud-monitoring --network "default" --subnetwork "default" --addons HorizontalPodAutoscaling,HttpLoadBalancing --no-enable-autoupgrade --no-enable-autorepair
gcloud beta container clusters create "gpu-cluster" --zone "us-central1-f" --username "admin" --cluster-version "1.10.5-gke.3" --machine-type "n1-standard-2" --accelerator "type=nvidia-tesla-v100,count=1" --image-type "COS" --disk-type "pd-standard" --disk-size "100" --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "2" --enable-cloud-logging --enable-cloud-monitoring --network "default" --subnetwork "default" --addons HorizontalPodAutoscaling,HttpLoadBalancing --no-enable-autoupgrade --enable-autorepair

## WORKED
gcloud beta container clusters create "gpu-cluster-v2" --zone "us-central1-f" --username "admin" --cluster-version "1.9.7-gke.3" --machine-type "n1-standard-2" --accelerator "type=nvidia-tesla-v100,count=1" --image-type "COS" --disk-type "pd-standard" --disk-size "100" --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "2" --enable-cloud-logging --enable-cloud-monitoring --network "default" --subnetwork "default" --addons HorizontalPodAutoscaling,HttpLoadBalancing --no-enable-autoupgrade --enable-autorepair

- Fetch credentials
gcloud container clusters get-credentials gpu-cluster-v2

- Fetch nodes info
kubectl get nodes -o wide                                                                                                                                                                                                                                             ✹ ✭
NAME                                            STATUS    ROLES     AGE       VERSION        INTERNAL-IP   EXTERNAL-IP      OS-IMAGE                             KERNEL-VERSION   CONTAINER-RUNTIME
gke-gpu-cluster-v2-default-pool-376ab26d-701d   Ready     <none>    43m       v1.9.7-gke.3   10.128.0.5    104.198.230.59   Container-Optimized OS from Google   4.4.111+         docker://17.3.2
gke-gpu-cluster-v2-default-pool-376ab26d-9mm3   Ready     <none>    43m       v1.9.7-gke.3   10.128.0.4    108.59.82.22     Container-Optimized OS from Google   4.4.111+         docker://17.3.2

- Install GPU drivers

COS image: kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/stable/nvidia-driver-installer/cos/daemonset-preloaded.yaml
Ubuntu image: kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/ubuntu/daemonset.yaml


- Init Helm
helm init
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
helm init --upgrade

- Install RabbitMQ
helm install stable/rabbitmq --name rabbitmq --set rabbitmq.username=guest,rabbitmq.password=guest

- Run Flask web server
kubectl apply -f flask-web.yml

- Run Fibonacci server
kubectl apply -f flask-fib.yml

- Expose Flask-web
kubectl expose deployment flask-web-deployment --type=NodePort --port=80 --target-port=8080 --name=flask-web

OR 

kubectl expose deployment flask-web-deployment --type=LoadBalancer --port=80 --target-port=8080 --name=flask-web-lb
service/flask-web-lb exposed

kubectl describe service flask-web-lb
Name:                     flask-web-lb
Namespace:                default
Labels:                   app=flask-web
Annotations:              <none>
Selector:                 app=flask-web
Type:                     LoadBalancer
IP:                       10.51.255.247
LoadBalancer Ingress:     35.226.12.108
Port:                     <unset>  80/TCP
TargetPort:               8080/TCP
NodePort:                 <unset>  30656/TCP
Endpoints:                10.48.0.11:8080,10.48.1.16:8080
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type    Reason                Age   From                Message
  ----    ------                ----  ----                -------
  Normal  EnsuringLoadBalancer  56s   service-controller  Ensuring load balancer
  Normal  EnsuredLoadBalancer   6s    service-controller  Ensured load balancer


- Extract the LoadBalancer IP
kubectl get service flask-web-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

- Do a gut check by calling Fibonacci service
http -v http://35.226.12.108/fib/20
OR 
http -v http://$(kubectl get service flask-web-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/fib/20

GET /fib/20 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: 35.193.183.126
User-Agent: HTTPie/0.9.9



HTTP/1.1 200 OK
Connection: close
Content-Length: 5
Content-Type: application/json
Date: Sat, 21 Jul 2018 20:47:55 GMT
Server: gunicorn/19.8.1

6765


- Run TensorFlow server
kubectl apply -f flask-neural.yml

- Test it!

- Spin it down!
gcloud container clusters delete gpu-cluster-v2

