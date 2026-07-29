
### Defined Service type Loadbalance , Auto triggers loadbalancer creation by the cloud,
Our app will be browsed with public ip of load balancer 
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: dep-loggen
  name: dep-loggen
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8000
  selector:
    app: dep-loggen
  type: LoadBalancer
status:
  loadBalancer: {}

```
## Why this impacts your /pingpong counter 

Because we  are using type: LoadBalancer, your service routes all incoming TCP traffic on port 80 directly to your pod's target port 8000.
- Without an Ingress Controller:No Path-Based Routing: Your LoadBalancer service cannot inspect paths like / vs /pingpong. It forwards raw HTTP requests straight to your container.Favicon & Auto-Requests: When you refresh [http://<LB-Public-IP>] in your browser:Browser requests GET  \ hits pod.Browser automatically requests GET /favicon.ico any of those secondary requests hitting port 8000 will cause the counter to increment on a page refresh.
#### Excercise 3.2  
WE will use both the app code built on FastAPI and ingress for routing based on ep.
---
#### For the cloud excercies we have used azure cloud
### Azure AKS Setup


```powershel
$RESOURCE_GROUP = "myResourceGroup"
$AKS_NAME = "myAKSCluster"
$LOCATION = "eastus"

# Create resource group ,  azure cli command
az group create --name $RESOURCE_GROUP --location $LOCATION    

# Create AKS cluster
az aks create --resource-group $RESOURCE_GROUP --name $AKS_NAME --node-count 1 --node-vm-size Standard_B2s --generate-ssh-keys

# Get cluster credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME



## Delete the cluster after activity
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

