## Static vs. Dynamic Volume

```
+----------------+
|  Administrator |
+-------+--------+
        |
        |---------------------------------------------+
        | (STATIC ROUTE)                              | (DYNAMIC ROUTE)
        | 1. Admin manually creates                   | 1. Admin creates
        |    Physical Disk (e.g., AWS EBS)            |    StorageClass only
        |    & PV YAML                                |
        v                                             v
+----------------+                          +------------------+
| PersistentVol  |                          |  StorageClass    |
|     ume (PV)   |                          | (Provisioner:    |
| [Manual YAML]  |                          |  ebs.csi.aws.com)|
+-------+--------+                          +--------+---------+
        |                                            |
        | 2. Developer requests                      | 2. Developer requests
        |    specific PV by name                     |    storage by class
        v                                            v
+----------------+                          +------------------+
| PersistentVol  |                          | PersistentVolume |
|  ume Claim     |                          |      Claim       |
|     (PVC)      |                          |      (PVC)       |
| volumeName:    |                          | storageClassName:|
|   "my-manual"  |                          |   "fast-ssd"     |
+-------+--------+                          +--------+---------+
        |                                            |
        | 3. Direct Bind                             | 3. System detects PVC
        |    (No new disk created)                   |    & triggers Provisioner
        |                                            v
        |                                   +------------------+
        |                                   |   Provisioner    |
        |                                   | (Cloud Provider) |
        |                                   +--------+---------+
        |                                            |
        |                                            | 4. Auto-create Disk & PV
        |                                            v
        |                                   +------------------+
        |                                   | PersistentVolume |
        |                                   | [Auto-Generated] |
        |                                   +--------+---------+
        |                                            |
        +--------------------+-----------------------+
                             |
                             | 5. Binding Complete
                             v
                    +------------------+
                    |       Pod        |
                    |  (Volume Mount)  |
                    +------------------+   

```

# Kubernetes Storage: Static vs. Dynamic Provisioning

## Overview
Kubernetes supports two methods for attaching persistent storage to pods:
1.  **Static Provisioning**: Administrators manually create PVs before users request them. 
2.  **Dynamic Provisioning**: Storage is created automatically when a user requests it via a StorageClass. 

---

## 1. Static Provisioning (Manual)
**Workflow**: Admin creates Disk $\rightarrow$ Admin creates PV $\rightarrow$ User creates PVC $\rightarrow$ Bind. 

### Step 1: Administrator creates the PV
The admin must manually provision the storage asset (e.g., via AWS Console) and define the PV YAML matching the specific volume ID. 

```yaml
# pv-static.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: manual-disk-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: manual  # Must match the PVC's class or be empty
  awsElasticBlockStore:     # Specific driver details required
    volumeID: vol-0a1b2c3d4e5f # The actual ID of the pre-created disk
    fsType: ext4   
```

#### Developer creates the PVC
```yaml
# pvc-static.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: manual-disk-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  volumeName: manual-disk-pv  # Explicitly binds to the existing PVCopied!   
```

## Step 2: Dynamic Provisioning (Automatic)
Workflow: Admin creates StorageClass $\rightarrow$ User creates PVC $\rightarrow$ System creates Disk & PV $\rightarrow$ Bind. 
#### Step 1: Administrator creates the StorageClass
```yaml
# storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer   
```
#### Step 2: Developer creates the PVC
```yaml
# pvc-dynamic.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: auto-disk-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd  # Triggers dynamic creation
  resources:
    requests:
      storage: 20Gi   
```

