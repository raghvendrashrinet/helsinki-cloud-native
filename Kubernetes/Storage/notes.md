## Kubernetes volumes
Kubernetes volumes provide a way for containers in a Pod to access and share data via the filesystem. 

#### 1. Transient Scratch Space: emptyDir
```
containers:
  - name: test-container
    image: registry.k8s.io/test-webserver
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir:
      sizeLimit: 500Mi
```


