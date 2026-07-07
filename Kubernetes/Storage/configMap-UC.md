### ConfigMaps
ConfigMaps are used to decouple environment-specific configuration from your container images. Use them for database hostnames, feature flags, logging levels, or configuration file templates.
a ConfigMap doesn't just store simple key-value pairs; how it is structured determines how your application consumes it.
### 1. Literal Key-Value Pairs (Property Injections)
It stores individual configuration properties as distinct keys, which are typically injected into the container as Environment Variables.
- **Real-World Use Case: Application Environment Tuning**
  Adjusting application behavior, external endpoints, or feature toggles between Development, Staging, and Production without changing the code.
  ConfigMap:
  ```yaml
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: payment-service-env
  data:
    ACCOUNTING_API_URL: "https://api.production.internal/v2"
    MAX_RETRIES: "5"
    FEATURE_FLAG_CRYPTO_PAY: "false"
  ```
  The Pod Manifest (Environment Injection)
  ```
  containers:
  - name: app
    image: company/payment-processor:v1.0
    env:
    - name: API_ENDPOINT
      valueFrom:
        configMapKeyRef:
          name: payment-service-env
          key: ACCOUNTING_API_URL
  ```
  #### 2. Entire Configuration Files (File Mounts)
  Instead of individual variables, a ConfigMap can hold entire, multi-line configuration files (like .yaml, .conf, .json, .ini). These are mounted into the container as physical files inside a directory.

  **Real-World Use Case: Reverse Proxy & Web Server Configurations**
  Injecting custom routing rules into standard image deployments like Nginx, Apache, or HAProxy.
 ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-routing-config
data:
  # The '|' character denotes a multi-line string block
  reverse-proxy.conf: |
    server {
        listen 80;
        server_name api.mycompany.com;

        location /v1 {
            proxy_pass http://v1-service.default.svc.cluster.local;
        }
        location /v2 {
            proxy_pass http://v2-service.default.svc.cluster.local;
        }
    }
  ```
 ###### The Pod Manifest (Volume Mount Injection)
 ```yaml
 containers:
  - name: nginx
    image: nginx:1.25
    volumeMounts:
    - name: config-volume
      mountPath: /etc/nginx/conf.d # Overwrites/places the file into this directory
  volumes:
  - name: config-volume
    configMap:
      name: nginx-routing-config
 ```
#### 3. Bulk Configuration (envFrom)
When an application requires dozens of environment variables, defining them line-by-line in a Pod specification creates massive manifest clutter. The envFrom type automatically grabs every single key inside a ConfigMap and maps it into the container as an environment variable.
**Real-World Use Case: Framework-Heavy Frameworks (e.g., Spring Boot / Django)**
Enterprise frameworks that rely on heavily mapped environment variables for database configurations, caching levels, session times, and external integrations.
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: legacy-crm-bulk-config
data:
  DB_USER: "crm_app"
  CACHE_TTL: "3600"
  SESSION_TIMEOUT: "30"
  DEBUG_MODE: "verbose"
  NOTIFICATIONS_ENABLED: "true"
```
###### The Pod Manifest (Bulk Mapping)
```yaml
containers:
  - name: server
    image: company/crm-platform:v4.2
    envFrom:
    - configMapRef:
        name: legacy-crm-bulk-config
```
Result: Inside the container, DB_USER, CACHE_TTL, SESSION_TIMEOUT, etc., are all instantly populated without needing separate definitions.

#### 4. Binary Data ConfigMaps (binaryData)
Standard ConfigMaps accept text encoded in UTF-8. If you need to inject non-textual assets—like a small image, a compressed zip file, or a custom binary license key—you use the binaryData field. The values must be explicitly base64 encoded.
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-assets
# Notice the field change from 'data' to 'binaryData'
binaryData:
  company_logo.png: iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=
  internal-certs.jks: zVvS0...[truncated base64 string]
```
###### Mounting Binary files
```yaml
containers:
  - name: java-runner
    image: eclipse-temurin:17
    volumeMounts:
    - name: binary-assets
      mountPath: /var/certs
  volumes:
  - name: binary-assets
    configMap:
      name: app-asset
```

---
#### Mounting Specific Files Safely (subPath)
Just like sharing files via emptyDir, using subPath allows you to inject a single configuration file into an existing folder without wiping out the surrounding directory's contents.

```yaml
spec:
  volumes:
  - name: config-volume
    configMap:
      name: nginx-config
  containers:
  - name: nginx
    image: nginx:alpine
    volumeMounts:
    - name: config-volume
      mountPath: /etc/nginx/nginx.conf # Exact target path
      subPath: nginx.conf              # Isolate this specific key/file
```
---
#### Imperative Commands
- From a literal value:
```
 kubectl create configmap app-inline-config --from-literal=APP_COLOR=blue --from-literal=MAX_CONNECTIONS=100
```
- From an entire local file:
```
 kubectl create configmap app-file-config --from-file=config.properties
```
---
When you update a ConfigMap or a Secret in Kubernetes, what happens to the injected values depends entirely on how you injected them into your Pods.  
Kubernetes does not automatically restart your pods when a ConfigMap or Secret changes.  
**Scenario 1: Injected as Environment Variables (env or envFrom)**
- What happens: ❌ Nothing changes inside the running container.
- Environment variables are strictly evaluated and injected only when the container starts up. If you update the ConfigMap or Secret on the cluster, the running application will continue to see the old values.
- `How to apply the change`: You must trigger a rolling restart of your deployment so new pods are created with the new values:
  ```
    kubectl rollout restart deployment/<deployment-name>
  ```
**Scenario 2: Mounted as Volumes (Without subPath)**
- What happens:  The files update automatically (eventually).
- The Kubelet daemon on the node watches for changes. Within a couple of minutes (depending on the Kubelet's sync cache interval, usually up to 60 seconds), the files inside your container’s mounted directory will quietly update to reflect the new data.
- Caveat: Your application code needs to be designed to actively re-read or "hot-reload" that file from disk when it changes  

**Scenario 3: Mounted as Files using subPath or subPathExpr**
 - What happens: ❌ The files will NOT update.
 -  The Details: When you use subPath,Kubernetes binds that specific file directly to the container at launch time. Because it is an isolated bind-mount, it breaks the connection to the automatic update utility. The file inside the container becomes completely static.
 -  Apply
   ```
   
    kubectl rollout restart deployment/<deployment-name>
   ```
### The Pro Way: Automated Restarts (Reloader)
If you want your deployment to automatically restart the moment a ConfigMap changes without you typing anything, the industry standard is to use an open-source tool called Reloader (by Stakater).

Once installed, you just add an annotation to your Deployment:

```YAML
metadata:
  annotations:
    reloader.stakater.com/auto: "true"
```

The moment you change the ConfigMap, Reloader triggers a rolling restart of your deployment automatically.

##### Why Companies Use It in ProductionIn a real enterprise environment, 
nobody manually types `kubectl rollout restart`. Instead, infrastructure is managed by `GitOps tools (like ArgoCD or FluxCD)` or `automated certificate managers (like cert-manager)`. Reloader acts as the missing automation link:
- Automated TLS Certificate Rotation: When cert-manager automatically renews an SSL/TLS certificate, it updates a Kubernetes Secret. Reloader detects this change and immediately kicks off a rolling restart of your Nginx, Ingress, or API pods so they pick up the new certificate before the old one expires.
- External Secret Managers: If a team rotates database passwords in HashiCorp Vault or AWS Secrets Manager, those sync down to native Kubernetes Secrets. Reloader ensures the backend application restarts instantly to use the new password, preventing application downtime.
- Safe, Non-Disruptive Rollouts: Reloader doesn't just crash your pods at once. It patches the deployment template and lets Kubernetes handle the rollout natively. This means it respects your configured RollingUpdate strategies, maxSurge, maxUnavailable, and PodDisruptionBudgets—ensuring zero downtime.

###### Note: To keep things safe in production, companies usually avoid turning on a blanket global auto-reload. Instead, they use scoped annotations so only specific workloads react to specific configuration changes
