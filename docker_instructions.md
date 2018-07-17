# Create Docker files for Neural Style Transfer app

---

**Install Helm Chart for RabbitMQ**


**Build Docker image**

`docker build  -t flask-web-server:0.1 --label flask-web-server -f Dockerfile-flask-webserver .`


**Tag for pushing to Harbor registry**

`docker tag flask-web-server:0.1 harbor.home.pcfdot.com/library/flask-web-server:0.1`


**Check the images locally**

```
docker images
REPOSITORY                                        TAG                 IMAGE ID            CREATED             SIZE
flask-web-server                                  0.1                 89c10e338b66        51 seconds ago      2.53GB
harbor.home.pcfdot.com/library/flask-web-server   0.1                 89c10e338b66        51 seconds ago      2.53GB
```


**Push to remote registry**
`docker push harbor.home.pcfdot.com/library/flask-web-server:0.1`


**Trial run**
`kubectl run flask --restart=Never --image=harbor.home.pcfdot.com/library/flask-web-server:0.1 -it /bin/bash`


**Get ready to run on k8s**


**Run App Server, Fibonacci Server and Neural Style Transfer TensorFlow server**
```
kubectl create -f flask-web-server.yml
kubectl create -f flask-fib-server.yml
kubectl create -f flask-neural-server.yml
kubectl get pods
NAME                  READY     STATUS    RESTARTS   AGE
flask-fib-server      1/1       Running   0          33m
flask-neural-server   1/1       Running   0          6m
flask-web-server      1/1       Running   0          54m
rabbitmq-0            1/1       Running   0          5h
```

---

**Make sure that k8s can trust harbor registry, by taking following action on all k8s worker nodes** 
(adding Harbor registry's CA cert to docker runtime)
```
cd /etc/docker/
mkdir -p certs.d/harbor.home.pcfdot.com
cd certs.d/harbor.home.pcfdot.com/
cat << EOF > ca.crt
-----BEGIN CERTIFICATE-----
MIIDUDCCAjigAwIBAgIUeEmyyEeKviLv5XIbOrTp9Srm3WswDQYJKoZIhvcNAQEL
BQAwHzELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Bpdm90YWwwHhcNMTgwMzE1MjA1
ODEwWhcNMjIwMzE2MjA1ODEwWjAfMQswCQYDVQQGEwJVUzEQMA4GA1UECgwHUGl2
b3RhbDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOy/Of5caTrF4HZm
b8895sm59Zn8bG2XIA/8Uu6u8NgguxI8zLvH1o7oN5QS5Tx+4BdMnhj1uom80lVO
X4lx7SoNIZrkNofZwoR9jBwDy/qNuOwT9coKYkmajWA3zWCMr7GilWl1Xezxa0U4
Rb8946ErTusif6266Ir6wI6O3p1n4xPFqUkC0HOxUAINYpQFHhA7QK/G08+zH8C0
MrFg/BkFSsA3QM5bZ4Gcg8IY5wjGhcwKaZHsM68SkmKbUPijzc5FcVgk/StI1qwy
/O7/7F02iY16RjaUQnA6dajI9wtOghGtDuXpXLIpKneMLUhicde02vZYwUHCW5ak
AsfZWbsCAwEAAaOBgzCBgDAdBgNVHQ4EFgQUl2wu0xbylBVGBH5kWlljF6Bn1okw
HwYDVR0jBBgwFoAUl2wu0xbylBVGBH5kWlljF6Bn1okwHQYDVR0lBBYwFAYIKwYB
BQUHAwIGCCsGAQUFBwMBMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgEG
MA0GCSqGSIb3DQEBCwUAA4IBAQBM5sneWH0bYR4WQSFt6HrmOLBHslFDiRWi5xCx
5gNqQ/Jsr+g2h3Wt7VmJ+0/yH4LsYoBAlsCqgjIxxwcLVxwj1JQxMSlqz80ybXPh
C7oss6tRkOvN6YmlaTRAhdvlPUNxzgm5/YGXJR0NVsPyLlNLj9P9k+TjUgjQhpvr
aGLN6UUG3w8lsXlgO4OHVnsRu9Byv/gg+3LyR+u/iCMM401jx8NmzCliHp/ObnBE
EbxeFBueNmGP4zELTpB1EPhibbGcemIvHW/Ub1U3sZdVK080tNbRf5URjNzGLxzy
kyN1oMij8aJRH3e2p0n+TrkFgL1LXkA2Y7KheUidcJMNfYrp
-----END CERTIFICATE-----
EOF
```

