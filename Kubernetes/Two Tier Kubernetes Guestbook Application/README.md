## Two Tier Kubernetes Guestbook Application
The classic Kubernetes Guestbook Application. Despite having three distinct deployments, it is functionally a Two-Tier Architecture: a Web Front-End Tier and a Redis Data Storage Back-End Tier.

### 🏛️ Architectural Overview
```
 [ User Browser / Client ]
                          │
                          ▼ (NodePort: 30009)
                 ┌──────────────────┐
                 │ frontend Service │
                 └────────┬─────────┘
                          │ (Round-Robin Load Balancing)
                          ▼
             ┌──────────────────────────┐
             │   FRONT-END TIER Pods    │
             │   (3 x PHP Web Server)   │
             └──────┬────────────┬──────┘
                    │            │
      (Write Requests)            (Read Requests)
                    │            │
                    ▼            ▼
         ┌────────────────┐    ┌─────────────────┐
         │  redis-master  │    │ redis-follower  │
         │    Service     │    │     Service     │
         └────────┬───────┘    └────────┬────────┘
                  │                     │
                  ▼                     ▼
         ┌────────────────┐    ┌─────────────────┐
         │ BACK-END TIER  │    │  BACK-END TIER  │
         │  (1 x Master)  │    │  (2 x Slaves)   │
         └────────┬───────┘    └─────────────────┘
                  │ (Data Replication)
                  └─────────────────────►
```
#### ⚙️ How the Tiers Function Together
1. The Front-End Tier (The Web Face)
   - The Pods: Three identical PHP web server replicas handle user traffic. They are stateless, meaning any user request can safely land on any of the three pods.
   - The Service (frontend): Acts as the external entry point. It uses a NodePort (30009), exposing the web app to the outside world through the IP address of any Kubernetes node.
   - DNS Discovery: The environment variable GET_HOSTS_FROM=dns tells the PHP code to look up the backend services (redis-master and redis-follower) using standard Kubernetes internal DNS names rather than hardcoded IP addresses.

#### 2. The Back-End Tier (The Data Store)
To handle scale and protect data, the Redis database is split into a Master-Slave (Leader-Follower) topology:
- The Redis Master (redis-master):
    * Role: Handles all data write and update actions.
    * Scaling: Exactly 1 replica. You can only have one master authoritatively processing state changes at a time to prevent data corruption ("split-brain").
    * Service: The redis-master service directs the front-end write requests straight to this single pod.
- The Redis Slaves (redis-slave / redis-follower):
    * Role: Handles all data read actions.
    * Data Replication: The slave pods continuously copy and synchronize data from the master pod in the background.
    * Scaling: 2 replicas. This distributes the heavy reading load away from the master and provides backup if one slave fails.
    * Service: The redis-follower service acts as a load balancer, splitting read requests equally between the two running slave pods.

#### End-to-End Data Flow
  - User Submits Data: A user opens their browser to port 30009, types a message, and clicks submit.
  - Web Routing: The frontend service routes the request to one of the 3 PHP pods.
  - Writing to DB: The PHP pod runs code that connects to the redis-master service on port 6379 to save the new entry.
  - Data Syncing: The Redis Master saves the item and immediately replicates it down to the 2 Redis Slave pods.
  - Reading the Page: When users refresh the page to view entries, the PHP pods request data from the redis-follower service, which quickly pulls the text from the nearest available slave pod.      
