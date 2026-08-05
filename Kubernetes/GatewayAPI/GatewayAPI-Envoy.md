##  Envoy Gateway

#### Setup Envoy in K3d

To get the Gateway working, you must install the cluster with the Traefik proxy disabled:
```
k3d cluster create --agents 2 -p 8081:80@loadbalancer --port 8082:30080@agent:0 --k3s-arg '--disable=traefik@server:0'
```
- Next step is to install Envoy. We opt here for the yaml based installation:
[Link](https://gateway.envoyproxy.io/docs/install/install-yaml/)
```
kubectl apply --server-side -f https://github.com/envoyproxy/gateway/releases/latest/download/install.yaml
kubectl -n envoy-gateway-system rollout status deployment/envoy-gateway --timeout=180s
```
- When you now define a gateway as follows:
```
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: eg
  listeners:
    - name: http
      protocol: HTTP
      port: 80

```
You can access the app root at the address http://localhost:8081, since in your k3d cluster the host port 8081 maps to the cluster load balancer port 80 and Envoy Gateway receives traffic on that path.