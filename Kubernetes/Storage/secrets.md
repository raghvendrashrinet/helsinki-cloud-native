
# Kubernetes Secrets: Comprehensive Guide & Use Cases

`Secrets` are designed to hold sensitive data like passwords, OAuth tokens, and SSH keys. Unlike ConfigMaps, data fields in a Secret manifest must be **Base64 encoded** (or created automatically via CLI).

---

## 1. Creating Secrets (Handling Base64 Coding)

### Use Case A: Declarative Manifest (`data` vs `stringData`)
* **Using `data`:** Values must be manually base64 encoded beforehand.
* **Using `stringData`:** Allows you to type plain text strings directly. Kubernetes converts them to base64 automatically under the hood when applied.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-db-secret
type: Opaque
stringData:
  DB_PASSWORD: "super-secret-password"  # Plain text (Kubernetes handles base64 transformation)
data:
  DB_USER: cm9vdA==                     # Manually encoded ("root")
```
### Use Case B: Creating via CLI (Recommended to avoid hardcoding strings)
```Bash
kubectl create secret generic app-db-secret --from-literal=DB_PASSWORD='super-secret-password'
```
### 2. Consuming Secrets in a Deployment
#### Use Case A: Injecting Secret Keys as Environment Variables
Safely populates database passwords or API keys directly into container variables.

```YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: api
        image: my-app:v1
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-db-secret
              key: DB_PASSWORD
```
#### Use Case B: Mounting Secrets as Sensitive Files
Commonly used for attaching TLS Certificates (tls.crt, tls.key) or service account JSON credential files.

```YAML
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: app-db-secret
  containers:
  - name: api
    image: my-app:v1
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
```

### 3. Specialized Secret Types
#### Use Case A: Container Registry Secret
(kubernetes.io/dockerconfigjson)
Used when your Kubernetes nodes need credentials to pull images from a private container registry (like private Docker Hub, GitHub Packages, Azure ACR).
```bash
kubectl create secret docker-registry private-registry-cred \
  --docker-server=[https://index.docker.io/v1/](https://index.docker.io/v1/) \
  --docker-username=my-user \
  --docker-password=my-password \
  --docker-email=my-email@example.com
```

Consuming the Private Registry Credential in a Deployment:

```yaml
spec:
  imagePullSecrets:
  - name: private-registry-cred
  containers:
  - name: webapp
    image: my-private-repo/secure-app:v1
```
#### Use Case B: TLS Secret (kubernetes.io/tls)
Used natively by Ingress Controllers (like Nginx or Traefik) to secure routing paths using SSL certificates
```
kubectl create secret tls webapp-tls-certs --cert=path/to/tls.crt --key=path/to/tls.key
```
