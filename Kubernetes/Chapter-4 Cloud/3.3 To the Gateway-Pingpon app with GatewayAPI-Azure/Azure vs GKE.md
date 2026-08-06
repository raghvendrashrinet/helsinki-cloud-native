## GKE
### GKE handles that exact scenario compared to Azure
1. What happens when you deploy an Ingress resource with no prior setup?
- On GKE: Unlike AKS, GKE has a built-in managed Ingress controller called GLBC (GCP Layer 7 Load Balancer Controller) running by default.

- When you submit an Ingress manifest, GKE automatically calls Google Cloud APIs behind the scenes and provisions an External HTTP(S) Load Balancer with a Public IP address—even without you manually installing an ingress controller.

- Requirements: For default GKE Ingress to work properly, your underlying Service must be configured as type: NodePort (or ClusterIP if you use Network Endpoint Groups/NEGs).

2. What happens when you create a type: LoadBalancer Service?
On GKE: Just like in Azure, the Kubernetes cloud controller manager detects the Service and provisions a Layer 4 (TCP/UDP) Network Load Balancer in Google Cloud.

A public Google IP is assigned directly to the Service, completely bypassing L7 HTTP routing, path-based rules, and Ingress resources


## Azure 
To deploy an Ingress and have it successfully provision a load balancer with a public IP on Azure (AKS), you need an Ingress Controller running in your cluster.

Here are the two standard ways to get it working in Azure:
#### Option 1: In-Cluster Controller (e.g., NGINX Ingress)
You install the NGINX Ingress Controller using Helm. Helm creates a Kubernetes Service of type: LoadBalancer, which prompts Azure to automatically provision a Layer 4 Azure Load Balancer with a Public IP.
 - 1. Install NGINX Ingress Controller via Helm:
 ```
 helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx
```
 - 2. Keep your Service as ClusterIP:
 ```
 apiVersion: v1
kind: Service
metadata:
  labels:
    app: logout
  name: logoutput-svc
spec:
  ports:
  - port: 2345
    protocol: TCP
    targetPort: 5000
  selector:
    app: logout
status:
  loadBalancer: {}
 ```
 - 3. Deploy your Ingress YAML (with ingressClassName: nginx):
 ```yaml
 apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: logoutput-svc
            port:
              number: 2345
 ```
 - 4. Verify the Public IP:
Running `kubectl get ingress` will now show the Azure Public IP created for the NGINX controller under the ADDRESS field.


#### Option 2: Native Azure Application Gateway (AGIC or Application Gateway for Containers)
If you want a fully managed, native Azure Layer 7 Load Balancer (Application Gateway) instead of running NGINX proxy pods inside your cluster:
- 1. Enable the AGIC addon when creating or updating your AKS cluster:
```
az aks enable-addons -g <ResourceGroup> -n <AKSClusterName> -a ingress-appgw --appgw-name myAppGateway --appgw-subnet-cidr "10.225.0.0/16"
```

- 2. Deploy your Ingress using the azure/application-gateway class:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-svc # Must be ClusterIP
            port:
              number: 80

```

#### Key Takeaway for Azure
Unlike GKE, which automatically provisions Google's L7 Load Balancer out of the box when you apply an Ingress, AKS requires you to install or enable an Ingress Controller (like NGINX or AGIC) first. Once installed, all your backend application Services stay as standard ClusterIP.
