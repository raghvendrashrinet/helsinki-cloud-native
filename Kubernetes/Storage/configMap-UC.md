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
