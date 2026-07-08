## Using Ingress instead of NodePort to access the project. 
#### Steps:
#### 1. Removed NodePort Service
#### 2. Create a cluster Service
```
 kubectl expose deployment dep-node-port --port=2345 --target-port=3000 --dry-run=client -o yaml > service.yaml
```
#### 3. Created Ingress 
```
### Path type prefix , matchec any
kubectl create ingress Ingress1 --rule=/*=dep-node-port:3000 --dry-run=client -o yaml > ingress.yaml


```
Ingress :
```
kubectl.exe get ingress
NAME       CLASS     HOSTS   ADDRESS                            PORTS   AGE
ingress1   traefik   *       172.19.0.2,172.19.0.3,172.19.0.5   80      56m
```
##### Traefik
Listening on : `0.0.0.0:8081->80/tcp (Traefik/Ingress)`


#### 4 Browse application on local machine
Since Ingress controller (Traefik) listens on port 80 inside the cluster, and k3d maps that to host port 8081
```
 http://localhost:8081
```


  `
