## 🧩 Gateway API Installation & Verification KB
Step 1: Verify CRDs are installed
Run:

bash
kubectl get crd | grep gateway.networking.k8s.io
You should see:

gatewayclasses.gateway.networking.k8s.io

gateways.gateway.networking.k8s.io

httproutes.gateway.networking.k8s.io
(and possibly tcproutes, grpcroutes, etc.)

👉 If these aren’t present, install CRDs first:

bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.0.0/crds.yaml
Step 2: Verify Envoy Gateway controller is running
bash
kubectl get pods -n envoy-gateway-system
Expect pods like:

envoy-gateway-xxxx

envoy-default-eg-xxxx

These are the controller and Envoy proxy pods.

Step 3: Verify GatewayClass
bash
kubectl get gatewayclass
Check:

Accepted: True

Controller name matches gateway.envoyproxy.io/gatewayclass-controller

Step 4: Verify Gateway
bash
kubectl get gateway -n default
Look for:

PROGRAMMED: True

An ADDRESS assigned (ClusterIP or LoadBalancer IP)

Step 5: Verify HTTPRoute
bash
kubectl get httproute -n default
kubectl describe httproute backend -n default
Check:

Accepted: True

ParentRefs → Gateway eg

Rules → backend Service port (e.g., 3000)

Step 6: Verify backend Service & Pod
bash
kubectl get svc,pods -n default
Confirm:

Service backend exists with port 3000

Pod backend-xxxx is Running and Ready

Step 7: Test traffic flow
Quick curl test (Linux/macOS/WSL):

bash
curl -H "Host: www.example.com" http://localhost:8082
PowerShell (Windows):

powershell
Invoke-WebRequest http://localhost:8082 -Headers @{Host="www.example.com"}
Browser test:  
Add to hosts file:

Code
127.0.0.1   www.example.com
Then open:

Code
http://www.example.com:8082