### Https Flow

Applycation(Listen HTTP) <-- SVC <-- Ingress(HTTPS definition and encrypt/decrypt)<-- Controller <-- User

The "HTTPS definition" lives entirely in a separate Kubernetes object called an Ingress.

Here is exactly how you split the files:

1. Your Application Manifest (deployment.yaml)
No HTTPS logic here. You simply define your app and which port it listens on internally.
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: my-app
        image: my-app-image
        ports:
        - containerPort: 8080  # App just speaks HTTP internally
```
2. The "HTTPS" Manifest (ingress.yaml)
This is where the magic happens. This is a separate file (or section) that tells Kubernetes: "Take traffic coming from the internet on HTTPS, decrypt it, and forward it to the app above."

This is the file that needs the special note for cert-manager:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    # THIS IS THE SPECIAL NOTE cert-manager watches for
    cert-manager.io/cluster-issuer: "letsencrypt-prod" 
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: my-app-tls-secret # Where cert-manager will save the cert
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-service # Connects to your Deployment above
            port:
              number: 8080
```
The Flow of Logic
You apply both files: kubectl apply -f deployment.yaml and kubectl apply -f ingress.yaml.
- Cert-manager ignores the deployment.yaml completely.
- Cert-manager sees the ingress.yaml, spots the annotation cert-manager.io/cluster-issuer, and creates the certificate.
The Ingress Controller (like NGINX) sees the tls section in ingress.yaml. It says: "Okay, I will listen on port 443 for app.example.com, grab the certificate from my-app-tls-secret, and forward traffic to port 8080."
Summary: Your app knows nothing about HTTPS. The Ingress Manifest is the only place you define HTTPS, and that is the only file that needs the cert-manager annotation.

####  Code in ingresss that specifies certificate
```yaml
annotations:
    # 1. This annotation triggers cert-manager to ACT
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  # 2. This section DEFINES the TLS requirement
  tls:
  - hosts:
    - app.example.com       # The domain you want to secure
    secretName: my-tls-secret # The name of the Secret where cert-manager will save the cert
```

##### How Cert-Manager Reads This
1. It scans spec.tls: Cert-manager looks at the hosts list (e.g., app.example.com) to know what domain to request a certificate for. 
2. It scans secretName: It looks at my-tls-secret to know where to save the certificate once it gets it.
 - If my-tls-secret does not exist: Cert-manager creates it, requests the certificate, and fills it.
 - If my-tls-secret exists: Cert-manager checks if the certificate inside is valid. If it is expiring soon, it renews it and updates the Secret. 
3. It connects the dots: It links the annotation (which Issuer to use) with the tls section (what domain to request) to perform the job. 

---
### cert-manager is configured by creating a specific Kubernetes resource called an Issuer or ClusterIssuer. 

 This resource tells cert-manager who to ask for certificates (e.g., Let's Encrypt) and how to prove you own the domain.

##### 1. Choose Your Scope: Issuer vs. ClusterIssuer
Issuer: Works only in the same namespace where it is defined.  Use this for single-tenant apps.
ClusterIssuer: Works cluster-wide (all namespaces).  Use this for shared infrastructure like a central Let's Encrypt configuration. 
##### 2. The Configuration YAML (Let's Encrypt Example)
You typically create a file named letsencrypt-prod.yaml. This defines the connection to the Certificate Authority. 
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer  # Use 'Issuer' if you want it namespace-scoped
metadata:
  name: letsencrypt-prod
spec:
  acme:
    # 1. The URL of the Certificate Authority
    server: https://acme-v02.api.letsencrypt.org/directory
    
    # 2. Your email (for expiration warnings from the CA)
    email: admin@example.com
    
    # 3. A secret name to store the ACME account private key
    # cert-manager creates this secret automatically upon first run
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    
    # 4. Challenge Solvers (How to prove domain ownership)
    solvers:
    - http01:
        ingress:
          # Must match your Ingress Controller class (e.g., nginx, traefik)
          ingressClassName: nginx
```
##### 3. Applying the Configuration
Run the following command to register this configuration with your cluster:
```
kubectl apply -f letsencrypt-prod.yaml
```
You can verify it is ready by running:

kubectl get clusterissuer letsencrypt-prod
# Output should show "READY" as "True"

4. How It Connects to Your App
Once this ClusterIssuer exists, your Ingress manifest references it by name:
```
metadata:
  annotations:
    # This links the Ingress to the ClusterIssuer defined above
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
```
Summary of Configuration Fields
- server: The API endpoint of the CA (Staging vs. Production). 
- privateKeySecretRef: Where cert-manager stores its own identity key (auto-created). 
- solvers: The method used for validation. HTTP-01 (via Ingress) is most common for public web apps; DNS-01 is used for wildcards (*.example.com) or internal networks.