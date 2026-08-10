# Step 1: Create GatewayClass
kubectl apply -f GatewayClass.yaml

# Step 2: Deploy applications
kubectl apply -f manifest/deployment_logout.yaml
kubectl apply -f manifest/deployment_pong.yaml

# Step 3: Expose services
kubectl apply -f manifest/service_logout.yaml
kubectl apply -f manifest/service_pong.yaml

# Step 4: Create Gateway
kubectl apply -f Gateway.yaml

# Step 5: Create routes
kubectl apply -f manifest/httproute.yaml

# Verify everything is ready
kubectl get all -n default
kubectl get gateway,httproute -n default