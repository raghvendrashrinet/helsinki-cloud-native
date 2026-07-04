## by default mounting , it will overwrite the directory content
#### Define the Shared emptyDir Volume
   ```
      volumes:
      - name: shared-logs
        emptyDir: {}
      containers:
      # 1. The Log Generator Container
      - name: log-generator
        image: raghvendrashrinet/projects:hashgenv1
        volumeMounts:
        - name: shared-logs
          mountPath: /app
```

#### Note : However, when Kubernetes mounts the emptyDir volume to the /app path in your container, it completely overlays and hides whatever was originally in that directory. Since emptyDir initializes completely empty, your code at /app/app.py disappears, resulting in the crash

1. mount your shared volume to a dedicated subfolder inside /app (such as /app/logs)
   - but for this to work ,programm logic should read and write to `/logs/log.txt`, which require changing the code
   - as its currently listening to WORDIR : /app
   ` mountPath: /app/logs`

2. We could use subPath
   ```
    volumeMounts:
        - name: myvol
          mountPath: /app/log.txt  # The exact path your script writes to
          subPath: log.txt
   ```
   #### rest will be same
   - Because Kubernetes is only replacing the exact file path /app/log.txt using subPath, your original container files (like app.py) inside /app remain completely untouched and visible.
   - o code changes required: Your Python scripts can continue to read and write directly to log.txt
  
3. #### Error : Kubernetes handles a subPath volume mount differently if the file doesn't already exist on the host.
 - When Kubernetes attempts to mount subPath: log.txt into your container, it looks inside the emptyDir volume for a file named log.txt. Because the emptyDir volume starts out completely empty, Kubernetes can't find that file. To prevent the mount from failing, Kubernetes automatically creates a fallback item at that path—but it defaults to creating a directory instead of an empty file.
 - As a result, /app/log.txt becomes a folder inside your container. When your Python script executes open("log.txt", "a"), it encounters a folder instead of a file, triggering the IsADirectoryError.

#### The Fix: Switch from subPath to subPathExpr with an Init Container
Since emptyDir cannot pre-create files natively, the cleanest and most robust Kubernetes pattern is to use a lightweight `Init Container `to create the empty log.txt file before your main containers start.
```
# 1. Init Container runs first to guarantee log.txt is a FILE, not a folder
      initContainers:
      - name: init-log-file
        image: busybox:stable
        command: ['sh', '-c', 'touch /mnt/shared/log.txt']
        volumeMounts:
        - name: myvol
          mountPath: /mnt/shared
```

### bypass k3d andaccess pod 
```
kubectl port-forward deployment/dep-loggen 8081:8000
```


### k3d setup
port 8081 on your local pc using k3d  is routed into the cluster's internal load balancer (Traefik) on port 80.
`0.0.0.0:8081->80/tcp`

##### 1. Create a Service (service.yaml)
```
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
  labels:
    app: dep-loggen
spec:
  selector:
    app: dep-loggen
  ports:
    - protocol: TCP
      port: 80         # Internal cluster port (what the service listens on)
      targetPort: 8000 # The actual containerPort your webapp runs on
```
##### 2. Create an Ingress (ingress.yaml)
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp-ingress
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp-service
            port:
              number: 80
```
```bash
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```
Open your web browser and go straight to:
`http://localhost:8081`

Get Container name using json path:
- Pod :`kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'`  
- Deployment : `kubectl get deployment dep-loggen -o jsonpath='{.spec.template.spec.containers[*].name}'`
