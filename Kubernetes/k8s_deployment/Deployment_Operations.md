# Kubernetes Deployments: Real-World Lifecycle & Operations Guide

A `Deployment` provides declarative updates for Pods and ReplicaSets. This guide captures the critical commands, update strategies, and day-2 operations used in production environments.

---

## 1. Production-Ready Deployment Blueprint

This template features standard labels, readiness/liveness probes, resource management, and rolling update tuning.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
  namespace: production
  labels:
    app.kubernetes.io/name: core-api
    app.kubernetes.io/part-of: e-commerce
spec:
  replicas: 3
  revisionHistoryLimit: 10 # Keeps last 10 versions for rollbacks
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%        # How many extra pods can be created during rollout
      maxUnavailable: 0    # Ensure 100% capacity is maintained during rollout
  selector:
    matchLabels:
      app: core-api
  template:
    metadata:
      labels:
        app: core-api
    spec:
      containers:
      - name: api-server
        image: nginx:1.25.1
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        readinessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
```
## 2. Rollout & Update Management
Any change to the Pod template (e.g., changing the image tag, labels, or environment variables) automatically triggers a rollout. Scaling replicas does not trigger a rollout.
#### Triggering a Rollout
  - The Standard Way (Declarative): Update the image tag in your YAML and run `kubectl apply -f deployment.yaml`.
  - The Imperative Way (Quick CI/CD update):
    ```
     kubectl set image deployment/core-api api-server=nginx:1.25.2
    ```
    `api-server is the name of the specific container inside your Pod that you want to update.`
  - The Manual Trigger (Forcing a restart): If you updated a ConfigMap or Secret and need the pods to pick up the changes, force a restart without configuration modifications:
  - ```
     kubectl rollout restart deployment/core-api
    ```
#### Monitoring Rollout Status
Track the live progress of a deployment update:
```
  kubectl rollout status deployment/core-api
```

## 3. Rollbacks & History Tracking
If a bad image tag or broken code is deployed, you can safely revert the cluster status.
- View Revision History:
  ```
    kubectl rollout history deployment/core-api
  ```
- Inspect a Specific Revision: Check what configuration was active in a historical revision (e.g., revision 2):
- ```
   kubectl rollout history deployment/core-api --revision=2
  ```
  ### Rollback
  - Rollback to the Immediate Previous Version
   ```
    kubectl rollout undo deployment/core-api
   ```
  - Rollback to a Specific Historical Revision:
   ```
    kubectl rollout undo deployment/core-api --to-revision=2
   ```

  ## 4. Scaling Operations
  **Manual Scaling**
  Modify the number of replicas running concurrently:
  ```
   kubectl scale deployment/core-api --replicas=5
  ```

  **Automated Scaling (Horizontal Pod Autoscaler - HPA)**
  Automatically scale replicas up and down dynamically based on target CPU utilization (requires Metrics Server in the cluster):
  ```
   kubectl autoscale deployment/core-api --min=3 --max=10 --cpu-percent=80
  ```
  
## 5. Pause & Resume (Canary/Debugging Workflows)
 When making multiple experimental configuration changes (e.g., modifying environment variables and shifting memory limit targets at the same time), you can pause the deployment tracking to avoid triggering multiple intermediate rollouts.
 1. Pause the Deployment:
  ```
   kubectl rollout pause deployment/core-api
  ```
 2. Apply multiple changes safely: (These changes stack up but will not spin up new Pods yet).
  ```
   kubectl set image deployment/core-api api-server=nginx:latest
   kubectl set resources deployment/core-api -c=api-server --limits=cpu=1
  ```
3. Resume the Deployment: Triggers a single, consolidated rolling update containing all changes.
  ```
   kubectl rollout resume deployment/core-api
  ```
---
## 6. Essential Troubleshooting Commands
When things go wrong during a deployment operation, use this sequence to diagnose the failure:
- Check Event Logs: See why the deployment is failing to schedule or pull images.
  ```
   kubectl describe deployment/core-api
  ```
- Inspect underlying ReplicaSets: The deployment manages intermediate ReplicaSets. If the deployment doesn't scale, check if the ReplicaSet has errors:
  ```
   kubectl get rs -l app=core-api
  ```
- View Aggregated Real-time Logs:
  ```
   kubectl logs -l app=core-api --tail=100 -f
  ```
  
