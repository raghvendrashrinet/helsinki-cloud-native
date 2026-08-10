## Gateway API in the k3d cluster
Gateway API is only a Kubernetes API specification. To actually handle traffic, you must install a Gateway implementation. There are many implementation options, for example, Envoy Gateway, NGINX Gateway Fabric, and Kong.

## Envoy Gateway
 it a Kubernetes-native API Gateway and reverse proxy control plane. It simplifies deploying and operating Envoy Proxy as a data plane by using the standard Gateway API and its own extensible APIs.

how Envoy Gateway implements the Gateway API:

```Text
+---------------------------+
|   Kubernetes Cluster      |
+---------------------------+
        |
        v
+---------------------------+
| Gateway API Resources     |
| - GatewayClass            |
| - Gateway                 |
| - HTTPRoute / TLSRoute    |
+---------------------------+
        |
        v
+---------------------------+
| Envoy Gateway Controller  |
| - Watches Gateway API CRDs|
| - Translates to Envoy xDS |
| - Adds Envoy Extensions   |
|   (Rate limiting, Auth)   |
+---------------------------+
        |
        v
+---------------------------+
| Envoy Proxy Data Plane    |
| - Listeners               |
| - Routes                  |
| - Filters                 |
+---------------------------+
        |
        v
+---------------------------+
| Application Services      |
+---------------------------+
```
Think of it as a pipeline:
- 1. You define traffic rules in Gateway API YAML.
- 2. Envoy Gateway reads those CRDs.
- 3. It translates them into Envoy config (xDS).
- 4. Envoy Proxy enforces those rules in the data plane.


#### To get the Gateway working,
  you must install the cluster with the Traefik proxy disabled:
  ```
  k3d cluster create --agents 2 -p 8081:80@loadbalancer --port 8082:30080@agent:0 --k3s-arg '--disable=traefik@server:0'
  ```

 ##### 1. Install with Helm Envoy Gateway
 ```
 helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.8.3 -n envoy-gateway-system --create-namespace
```
Wait for Envoy Gateway to become available:
```
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available

```
 ##### 2. Now Install the GatewayClass, Gateway, HTTPRoute and example app:


Event Sequence 
 1.Helm install Envoy Gateway → this chart automatically installs the Gateway API CRDs (that’s why you didn’t see them in your manifest).
2, en you applied your manifest with GatewayClass, Gateway, HTTPRoute, etc. → Kubernetes recognized them because the CRDs were already present.

3. Envoy Gateway controller watches those CRDs and reconciles them into Envoy proxy config.

```
kubectle apply -f \manifest\
```


