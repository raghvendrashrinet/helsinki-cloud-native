### Azure AKS Ingress Configuration
#### 1. Using Helm

1. - Add the Kubernetes community NGINX ingress repository to your local Helm client and pull the latest index
  ```bash
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm repo update
  ```
2. - Extract the AKS Node Resource GroupWhen Helm tells Kubernetes to create a LoadBalancer service, Azure builds a public IP inside the AKS managed node resource group. Grab this group name via the Azure CLI so you can reference it during installation:

  ```bash
  # Replace myResourceGroup and myAKSCluster with your names
  NODE_RG=$(az aks show -g myResourceGroup -n myAKSCluster --query nodeResourceGroup -o tsv)
  ```
3. - Install the Ingress Controller via Helm
Run the helm install command. The --set parameters explicitly attach Azure cloud-specific annotations so the cloud provider routes traffic correctly

  ```bash
  helm install aks-ingress ingress-nginx/ingress-nginx \
    --create-namespace \
    --namespace ingress-basic \
    --set controller.replicaCount=2 \
    --set controller.service.externalTrafficPolicy=Local \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"="$NODE_RG"
    ```
>[!NOTE]
>--set controller.replicaCount=2: Deploys two replicas for high availability.  
>--set controller.service.externalTrafficPolicy=Local: Preserves client source IPs.  
>--set ...azure-load-balancer-resource-group: Directs Azure to create the public IP in the correct managed node resource group.
 4. - Verify the Public IP Assignment
  ```
  kubectl get service -w aks-ingress-ingress-nginx-controller --namespace ingress-basic
  ```


---
### Using Azure Method
##### enable the Application Routing Add-on for Azure Kubernetes Service (AKS).This add-on automates the deployment of a fully managed NGINX Ingress Controller and integrates it with Azure Private DNS and Azure Key Vault for SSL/TLS management
1. - Enable Application Routing on AKSRun the following Azure CLI command to enable the managed NGINX Ingress Controller on your existing AKS cluster.
  ```
  az aks approuting enable \
  --resource-group myResourceGroup \
  --name myAKSCluster
  ```
2. - Verify the Ingress Controller Deployment
   ```
   # Check the deployment pods
    kubectl get pods -n app-routing-system

   # Find your public External IP address
    kubectl get svc -n app-routing-system
   ```
   > Take note of the` EXTERNAL-IP `generated for the nginx service, as this will route external traffic into your cluster.
3. - Deploy an Application and Ingress Route
     To test the setup, save the following configuration as app-ingress.yaml. This file creates a sample web application, a target service, and the Ingress routing rule.yamlapiVersion: apps/v1
```yaml
kind: Deployment
metadata:
  name: sample-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
    spec:
      containers:
      - name: web
        image: ://microsoft.com
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: sample-service
spec:
  type: ClusterIP
  ports:
  - port: 80
  selector:
    app: sample-app
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sample-ingress
  annotations:
    # This annotation attaches the ingress rule to the managed controller
    kubernetes.io/ingress.class: ://azure.com
spec:
  rules:
  - host: ://example.com  # Replace with your domain name
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sample-service
            port:
              number: 80
```
   
---
### checking nodepool 
```
 az aks nodepool list --resource-group rg1  --cluster-name myAKSCluster  --output table
```
