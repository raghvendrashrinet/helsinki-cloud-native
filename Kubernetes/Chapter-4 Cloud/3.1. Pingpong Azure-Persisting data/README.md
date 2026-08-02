## For Azure Cloud persiting Data added pvc with Storage class auto provisioned by Azure
[Azure-StorageClass](Azure-StorageClass.md)

 ####  Logic 
- Define PVC : `manifest/pvc.yaml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-managed-disk-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: azurefile-csi
  resources:
    requests:
      storage: 1Gi 
```
- Update Deployment.yaml : Stoarge type pvc
    ```
     persistentVolumeClaim:
            claimName: azure-managed-disk-pvc
    ```
- Create the resources
     ```
        kubectl apply -f pv.yaml
        
     # check the pvc bound
     ```
####  Once PVC Bound Deploy resources 
       ` kubectl apply -f deployment.yaml`

  ### Check the app
  ```
    # Verify the Azure LoadBalancer service
    kubectl get svc dep-loggen
  ```
  ### Browse via Azure LoadBalancer
  - Access the app using the external IP assigned by Azure:
    `http://<EXTERNAL-IP>/`
  - This project uses `type: LoadBalancer` in `svc.yaml`, so Azure will provision the LB and expose the service.

#### Troubleshoot
- Check log in the local 
` ocker exec k3d-k3s-default-agent-0 tail -f  /tmp/kube/log.txt`
- check log in app
  ` kubectl.exe exec -it dep-loggen-7cfbb6658d-2ch6d  -c webapp -- tail -f /app/log.txt`
     
---
## Storage Logic
### The Init Container Perspective
The init container's job is just to write an empty file into the shared emptyDir volume. It doesn't know or care about the /app folder
```
 initContainers:
  - name: init-log-file
    image: busybox:1.36
    command: ['sh', '-c', 'touch /mnt/shared/log.txt'] # <-- Created here
    volumeMounts:
    - name: myvol
      mountPath: /mnt/shared # <-- Matches the touch command path
```


### 2. The WebApp Container Perspective
When the main application container starts, it mounts that exact same myvol volume, but maps it to its own internal location (/app/log.txt) using subPath.
 

```
containers:
  - name: webapp
    image: my-web-app:v1
    volumeMounts:
    - name: myvol
      mountPath: /app/log.txt  # <-- Where your app code looks for it
      subPath: log.txt         # <-- Points directly to the file init created
```
---