## Pod Scheduling



progression from NodeSelector → Node Affinity → Advanced Scheduling
```
+---------------------------------------------------+
|                 Pod Scheduling Flow               |
+---------------------------------------------------+
        |
        v
+-------------------+
|   NodeSelector    |   <-- Basic: exact label match
|   (key=value)     |
+-------------------+
        |
        v
+-----------------------------+
|       Node Affinity         |   <-- Intermediate: flexible rules
|  - requiredDuringScheduling |
|  - preferredDuringScheduling|
+-----------------------------+
        |
        v
+-----------------------------------+
|   Advanced Scheduling Features    |
|                                   |
|  + Pod Affinity / Anti-affinity   |
|  + Taints & Tolerations           |
|  + Topology Spread Constraints    |
+-----------------------------------+
```


### The first and most basic way to control Pod placement is with a nodeSelector. Let’s start from there and build up step by step.

#### 🟢 Step 1: NodeSelector (Basic)
Purpose: Match Pods to nodes with specific labels.

Manifest Example:
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx
  nodeSelector:
    disktype: ssd
```
** Requirement: Node must be labeled first : `kubectl label nodes <node-name> disktype=ssd`

#### 🟡 Step 2: Node Affinity (Intermediate)
Purpose: More expressive rules than nodeSelector.

Types:

- `requiredDuringSchedulingIgnoredDuringExecution` → Hard rules, Pod won’t schedule if unmet.

- `preferredDuringSchedulingIgnoredDuringExecution` → Soft rules, scheduler prefers but can fall back.

Example (Required):
```
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: disktype
          operator: In
          values:
          - ssd
```

#### 🔵 Step 3: Advanced Node Affinity
*Operators*: `In, NotIn, Exists, DoesNotExist, Gt, Lt.`

Combine rules: Mix required + preferred affinities.

Multi-label matching: Require multiple labels (e.g., region=us-east AND disktype=ssd).

Example (Preferred with weight):
```
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 1
      preference:
        matchExpressions:
        - key: zone
          operator: In
          values:
          - us-east-1a
```
**Weight:** In `preferredDuringSchedulingIgnoredDuringExecution`, you can define multiple preferences for node selection. 
 - An integer (1–100) that indicates how strongly the scheduler should prefer that rule compared to others.
 - The scheduler calculates a score for each node based on all preferences. Nodes with higher scores are more likely to be chosen.
#### 🔴 Step 4: Beyond Node Affinity
- Pod Affinity & Anti-affinity → Control Pod-to-Pod placement.

- Taints & Tolerations → Repel or attract Pods to nodes.

- Topology Spread Constraints → Distribute Pods evenly across zones/nodes.
---

## 🟡 Taints & Tolerations Explained
- **Taint (on node)**: Marks a node as undesirable for Pods unless they explicitly tolerate it.
   Example:
  ```
    kubectl taint nodes node1 key=value:NoSchedule
  ```
  → This says: “Don’t schedule Pods here unless they tolerate` key=value:NoSchedule.”`
  
- **Toleration (on Pod)**: Declares that the Pod can run on tainted nodes.
   Example: Pod Config
  ```
   tolerations:
   - key: "key"
     operator: "Equal"
     value: "value"
     effect: "NoSchedule"
  ```
  → This says: “I accept the taint key=value:NoSchedule.”
  
### 🔎 Effects
- **NoSchedule:** Pod won’t schedule unless toleration matches.

- **PreferNoSchedule:** Scheduler avoids node but can place Pod if needed.

- **NoExecute:** Evicts existing Pods unless they tolerate the taint.

### 🚫 The Magic Effect: NoExecute
If you apply a taint with the NoExecute effect, Kubernetes will immediately evict ("pull out") any running Pods that do not tolerate this taint.
`kubectl taint nodes <node-name> key=value:NoExecute`
 - Any Pod on that node without a matching toleration is evicted immediately
 - Pods with a matching toleration will stay.

*NoSchedule & PreferNoSchedule* -> They only affect new scheduling decisions
### 💡 Alternative: kubectl drain
If your goal is to safely empty a node completely (for maintenance or because it is failing), the standard best practice is to drain the node instead of manually applying a taint:
```
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

