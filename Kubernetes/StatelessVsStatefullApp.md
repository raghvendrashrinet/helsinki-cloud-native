### Statefull Vs Stateless Apps
##### Stateless apps: 
- Usually don’t need persistent volumes. If they do, use RWX-capable storage (like NFS/EFS/Azure Files) so all replicas can mount.

##### Stateful apps:
- Use StatefulSets with per-Pod PVCs for durable, isolated storage.

>[!NOTE]
>In practice:  
>If you deploy a web app with 3 replicas and mount an `EBS volume (RWO)`, only one Pod will get scheduled with that volume.  
> If you instead use EFS (RWX), all 3 Pods can mount the same volume simultaneously.

#### stateless app replicas mount shared storage versus stateful apps with per‑pod volumes:
```
                Stateless Deployment (3 replicas)
                ---------------------------------
                 +---------+     +---------+     +---------+
                 | Pod A   |     | Pod B   |     | Pod C   |
                 |---------|     |---------|     |---------|
                 |  App    |     |  App    |     |  App    |
                 +---------+     +---------+     +---------+
                      |               |               |
                      +---------------+---------------+
                                      |
                               +-------------+
                               | RWX Volume  |
                               | (EFS/NFS)   |
                               +-------------+


                StatefulSet (3 replicas)
                ------------------------
                 +---------+     +---------+     +---------+
                 | Pod 0   |     | Pod 1   |     | Pod 2   |
                 |---------|     |---------|     |---------|
                 |  DB     |     |  DB     |     |  DB     |
                 +---------+     +---------+     +---------+
                      |               |               |
               +-------------+  +-------------+  +-------------+
               | PVC-0       |  | PVC-1       |  | PVC-2       |
               | (EBS/Disk)  |  | (EBS/Disk)  |  | (EBS/Disk)  |
               +-------------+  +-------------+  +-------------+
```

##### Explanation

- `Stateless apps:` All replicas can mount the same shared RWX volume (like NFS/EFS/Azure Files) simultaneously.

- `Stateful apps:` Each replica gets its own dedicated PVC, ensuring isolated persistent state per Pod.

##### 📦 Storage Access Modes
`RWO (ReadWriteOnce)`

A volume can be mounted by only one Pod at a time (on one node).
- Typical for block storage (EBS, Azure Disk, GCE Persistent Disk).Good for stateful apps where each Pod needs its own dedicated disk.

- `RWX (ReadWriteMany)`
A volume can be mounted by multiple Pods simultaneously (across nodes).  
Typical for shared filesystems (NFS, EFS, Azure Files, CephFS).
Useful for stateless apps with replicas that need shared config/logs.


#### 🔵 Stateful Apps
-------------------------------------------------
- Each Pod needs its own persistent state.
- Managed via StatefulSets with volumeClaimTemplates.
- Each Pod gets its own RWO PVC (isolated disk).
- Each Pod also gets a **unique, stable network identity**:
    • Pod names: db-0, db-1, db-2
    • PVCs: db-data-db-0, db-data-db-1, db-data-db-2
- Example: 3 replicas of a database, each with its own disk
  and unique name for durability + identity.
-------------------------------------------------

#### StatefulSet (Database Example)
```
-------------------------------------------------
   +---------+        +---------+        +---------+
   | Pod db-0|        | Pod db-1|        | Pod db-2|
   +---------+        +---------+        +---------+
        |                  |                  |
   +----------------+  +----------------+  +----------------+
   | PVC db-data-0  |  | PVC db-data-1  |  | PVC db-data-2  |
   | (RWO Volume)   |  | (RWO Volume)   |  | (RWO Volume)   |
   +----------------+  +----------------+  +----------------+
```
Key Points:
- Each Pod has a **unique, stable name** (db-0, db-1, db-2).
- Each Pod gets its own **dedicated RWO PVC** bound to that name.
- When Pod db-1 restarts, it always reattaches to PVC db-data-1.
- Ensures isolated persistent state and durability.
---

```
StatefulSet with Headless Service
-------------------------------------------------
   +---------+        +---------+        +---------+
   | Pod db-0|        | Pod db-1|        | Pod db-2|
   +---------+        +---------+        +---------+
        |                  |                  |
   +----------------+  +----------------+  +----------------+
   | PVC db-data-0  |  | PVC db-data-1  |  | PVC db-data-2  |
   | (RWO Volume)   |  | (RWO Volume)   |  | (RWO Volume)   |
   +----------------+  +----------------+  +----------------+
        |                  |                  |
        +------------------+------------------+
                           |
                  +-------------------+
                  | Headless Service  |
                  | (ClusterIP=None)  |
                  +-------------------+
                           |
   DNS resolves to each Pod directly:
   db-0.db-service.namespace.svc.cluster.local
   db-1.db-service.namespace.svc.cluster.local
   db-2.db-service.namespace.svc.cluster.local
```
**Unique Names:** Pods in a StatefulSet are ordered and named predictably (db-0, db-1, db-2).

**RWO PVCs:** Each Pod gets its own dedicated disk (db-data-0, db-data-1, db-data-2).

**Headless Service:** Created with clusterIP: None. Instead of load-balancing, it exposes DNS records for each Pod.
  - Clients can connect directly to db-0, db-1, db-2 using DNS
