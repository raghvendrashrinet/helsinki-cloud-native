## What the app does
1. Fetches a Random Image: It gets a placeholder image from the Lorem Picsum API (https://picsum.photos). 
2. Caches the Image URL: It stores the image URL and a timestamp in a JSON file (/data/image_cache.json). 
3. Enforces a 10-Minute TTL:
If the cache is younger than 10 minutes, it serves the same image to every user.
If the cache is older than 10 minutes, it fetches a new random image and updates the cache. 
4. Persists Data: It saves the cache to a Persistent Volume (PV) mounted at /data.  This ensures the cache survives if the Kubernetes pod crashes or restarts.

---
Infra 

1. Deployed PV of type Local to store the image cache on the local node disk
   in the 
   - First make a directory ` /tmp/kube` on node `  k3d-k3s-default-agent-0'
   - NodeSelector Part: it ensure to create pod on  k3d-k3s-default-agent-0
   - If the node specified in your nodeAffinity (e.g., k3d-k3s-default-agent-0) is not schedulable (e.g., it is cordoned, tainted, out of resources, or down), your pod will remain stuck in a Pending state indefinitely
```
   local:
    path: /tmp/kube
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k3d-k3s-default-agent-0
```

   2. Deploy all resources in the maifest folder
   3. Once all resource are up , browse `http://localhost:8081/`
