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

---
### Data Persistence : local/ hostpath

to achieve persistence switch from emptyDir to either hostPath or local volumes
- `local Volumes (Recommended)`: Kubernetes is fully aware of where this data lives. If your Pod dies, the scheduler ensures the replacement Pod is sent back to the exact same node where your data is.
- `hostPath Volumes (Use with Caution)`: Kubernetes has no cluster-wide awareness of this path. If you have a multi-node cluster and your Pod gets rescheduled to a different node, it will look for the same directory path there—finding it completely empty or non-existent.

#### Upgrading to a local Volume
To use a local volume properly, you define a cluster-level `PersistentVolume (PV)` that targets a directory on your node, and then your Pod requests it via a` PersistentVolumeClaim`(PVC)

##### Storage Class :StorageClass acts as a blueprint or template that automates the provisioning of persistent storage.

Instead of an administrator manually logging into a cloud console to carve out a virtual disk every time a developer asks for storage, the StorageClass handles it automatically behind the scenes.
1. Dynamic Provisioning (No More Manual Work)
   Without a StorageClass, an administrator has to pre-create a pool of physical disks (PersistentVolumes). With a StorageClass, when a user creates a PersistentVolumeClaim (PVC), the cluster automatically talks to your cloud or storage provider (AWS, GCP, Azure, Ceph, etc.) and spins up the disk on demand.
2. Abstracting Infrastructure
Developers don't need to know whether the application is running on AWS, Azure, or an on-premise data center. They just ask for a StorageClass by name (e.g., fast-storage), and Kubernetes handles the cloud-specific details.
3. Tiered Storage Quality
You can define multiple StorageClasses to offer different tiers of performance and cost:
* gold: High-speed SSDs (gp3 / premium-ssd) for databases.
* silver: Standard HDDs for logs or backup files.

##### Step 1: Create a StorageClass
This tells Kubernetes to wait until a Pod is scheduled before binding the storage.
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner # aws provisioner kubernetes.io/aws-ebs
volumeBindingMode: WaitForFirstConsumer
```
##### Step 2: Define the PersistentVolume (PV)
This maps out the physical folder on your node (e.g.,` /mnt/disks/my-project-data`) and locks it to a specific node using nodeAffinity.
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: project-local-pv
spec:
  capacity:
    storage: 10Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/my-project-data # Path on your physical node
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - my-node-name # Change to your actual node name
```
##### Step 3: Define the PVC and Update your Pod
Your Pod no longer cares about the underlying infrastructure; it just asks for the claim.
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-storage-claim
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: my-project-pod
spec:
  containers:
  - name: app-container
    image: your-app-image
    volumeMounts:
    - mountPath: /data # Inside the container
      name: data-volume
  volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: project-storage-claim
```
