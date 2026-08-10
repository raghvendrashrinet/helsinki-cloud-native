# Azure AKS Ingress Options

## 1. Auto-Provisioning: Azure Application Routing Add-on (Recommended)

**Key Characteristics**
- Management: Fully managed by Azure (updates, scaling, health)
- Namespace: `app-routing-system`
- Ingress Class Name: `webapprouting.kubernetes.azure.com`  
  *(Critical: `nginx` will not work)*
- Best For: Production workloads needing low maintenance, integrated DNS, managed SSL

**Enable**
```bash
az aks approuting enable --resource-group <YourResourceGroup> --name <YourClusterName>

Ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: project
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80

```
---
## 2. Manual Provisioning: Community NGINX via Helm
Key Characteristics

Management: Self-managed (you handle upgrades, patches, troubleshooting)
- Namespace: ingress-basic or ingress-nginx
- Ingress Class Name: nginx

Best For: Development, custom configs, avoiding Azure lock-in
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-basic \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz

```

Ingress YAML
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: project
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```