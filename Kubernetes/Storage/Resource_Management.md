# Kubernetes Resource Management: Requests, Limits, Quotas, and LimitRanges

Managing compute resources (CPU and Memory) is critical for cluster stability. This guide covers how to request resources for individual containers, enforce boundaries across a namespace, and automate defaults.

---

## 1. Container Level: Resource Requests vs. Limits

Every container in a Pod can declare its compute resource requirements using `requests` and `limits`.

*   **`requests` (The Guarantee):** The minimum amount of CPU/Memory the container needs to run. The Kubernetes scheduler uses this number to find a node that has enough free space. If no node has this capacity, the Pod stays `Pending`.
*   **`limits` (The Ceiling):** The maximum amount of CPU/Memory the container is allowed to consume.
    *   **Memory Exceeded:** The container is instantly killed by the kernel (`OOMKilled`).
    *   **CPU Exceeded:** The container is **throttled** (slowed down) via the Linux kernel's Completely Fair Scheduler (CFS), but it is not terminated.

### Full Example Manifest (`deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-resources
  labels:
    app: webapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: web-server
        image: nginx:alpine
        resources:
          requests:
            memory: "256Mi"   # 256 Mebibytes guaranteed
            cpu: "250m"       # 250 millicores (0.25 of a core)
          limits:
            memory: "512Mi"   # Max memory allowed before OOM kill
            cpu: "500m"       # Max CPU allowed before throttling kicks in
```
---
## 2. Namespace Level: Resource Quota
A ResourceQuota sets a hard ceiling on the total aggregate resources consumed by all Pods running inside a specific namespace. It protects the cluster from a single namespace consuming all physical hardware.
#####  The Golden Rule: The moment a ResourceQuota is applied to a namespace, every single Pod deployed there must explicitly define its own requests and limits, or the API server will reject it.
resource-quota.yaml
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: staging
spec:
  hard:
    pods: "10"                # Maximum of 10 pods total in this namespace
    requests.cpu: "2"         # Sum of all CPU requests cannot exceed 2 cores
    limits.cpu: "4"           # Sum of all CPU limits cannot exceed 4 cores
    requests.memory: 4Gi      # Sum of all Memory requests cannot exceed 4Gi
    limits.memory: 8Gi        # Sum of all Memory limits cannot exceed 8Gi
    services: "5"             # Max 5 Services allowed
```

## 3. Automation Level: LimitRange (LimitRanger)
To prevent developers from having their manifests rejected by the ResourceQuota if they forget to type the resources block, a LimitRange automatically injects defaults. It also enforces minimum and maximum sizes for individual containers.
 limit-range.yaml
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: staging
spec:
  limits:
  - type: Container
    # 1. Default Injections (Injected automatically if deployment.yaml leaves them blank)
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "256Mi"
    
    # 2. Strict Boundaries (Deployments will be rejected if they fall outside these numbers)
    max:
      cpu: "2"                # No individual container can ask for more than 2 cores
      memory: "2Gi"           # No individual container can ask for more than 2Gi memory
    min:
      cpu: "50m"              # No individual container can ask for less than 50m
      memory: "64Mi"          # No individual container can ask for less than 64Mi
```
| Component | Scope | Main Purpose | Action on Violation |
| :--- | :--- | :--- | :--- |
| **Requests/Limits** | Container | Controls individual runtime performance. | Memory triggers `OOMKilled`; CPU triggers Throttling. |
| **ResourceQuota** | Namespace | Total boundary protection for shared clusters. | Rejects new deployments outright. |
| **LimitRange** | Container/Pod | Auto-injects defaults and guards min/max boundaries. | Auto-corrects missing fields or rejects invalid sizes. |
