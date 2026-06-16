# Real-World Docker Compose Cheat Sheet

A curated list of the most frequently used Docker Compose commands in day-to-day development, debugging, and production workflows.

---

## 1. Lifecycle & Container Management

### Up (Start everything)
Builds, (re)creates, starts, and attaches to containers for a service.
* **Standard background run (Most Common):**
    ```bash
    docker compose up -d
    ```
    *The `-d` flag runs containers in detached mode (in the background), freeing up your terminal.*

### Down (Stop and clean up)
Stops containers and removes containers, networks, volumes, and images created by `up`.
* **Standard stop:**
    ```bash
    docker compose down
    ```
* **Hard reset (Wipe volumes):**
    ```bash
    docker compose down -v
    ```
    *The `-v` flag deletes all persistent data volumes (e.g., wiping database states to start completely fresh).*

### Start / Stop (Pause state)
Stops or starts services without destroying the containers or clearing ephemeral internal data.
```bash
docker compose stop
docker compose start
```
### docker compose cp
```
docker compose cp backend:/app/dumps/heap_dump.hprof ./local_dumps/
```
### iamge list 
`docker compose images`



### 1. Pull the absolute latest images from the registry
docker compose pull

### 2. Shut down everything, wipe old volumes, and clear orphaned services
docker compose down -v --remove-orphans

### 3. Force a build of local code changes and launch in the background
docker compose up -d --build

### 4. Stream the live logs of the backend to verify it started successfully
docker compose logs -f backend
