# Docker Data Persistence
## Docker Volumes : Volumes vs. Bind Mounts
By default, all files created inside a container are stored on a writable container layer. This means that if the container is deleted, the data is lost. To persist data, Docker provides two primary mechanisms: **Volumes** and **Bind Mounts**.

---

## 1. Docker Volumes (Recommended)
Volumes are completely managed by Docker and are stored in a dedicated directory on the host machine (e.g., `/var/lib/docker/volumes/` on Linux). 

### Key Characteristics:
* **Managed by Docker:** You don't need to worry about the underlying host file system structure.
* **Isolated:** Non-Docker processes on the host machine should not modify this data directory.
* **Safe for Sharing:** Multiple running containers can safely share the same volume simultaneously.
* **Easy to Back Up:** Can be backed up, migrated, or encrypted easily using Docker CLI commands.

### Quick Commands:
```bash
# Create a volume
docker volume create my_data
```
# Start a container using the volume , Mounting the volume
The syntax follows a [source]:[destination] format:
```
docker run -d --name app -v my_data:/app/data nginx
```
Note: Mostly docker volumes are used

Example : yt-dlp project with downloading yuotube vedio


```Dockerfile
FROM ubuntu:24.04

WORKDIR /mydir

#DEBIAN_FRONTEND environment variable to noninteractive,This tells apt to automatically accept default values (usually UTC) instead of asking for your geographic area
RUN export DEBIAN_FRONTEND=noninteractive &&     apt-get update &&     apt-get install -y curl python3 ffmpeg

# Downloading yt-dlp package in /usr/local/bin/ folder for executable path
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp

# Change permission
RUN chmod +x /usr/local/bin/yt-dlp

ENTRYPOINT ["/usr/local/bin/yt-dlp"]

#now build and run as below
#$ docker build -t yt-dlp .
#$ docker run yt-dlp https://www.youtube.com/watch?v=uTZSILGTskA


CMD ["https://www.youtube.com/watch?v=saEpkcVi1d4"]
```
Build image and mount the current volume to the container 
> docker build -t yt-dlp .
- Mounts a whole directory
```bash
docker run -v "$(pwd):/mydir" yt-dlp https://www.youtube.com/watch?v=saEpkcVi1d4
```
- Mounting only a file, to be able to modify from host and container both,
```bash
  -v "$(pwd)/material.md:/mydir/material.md"
```

Example 2 A container writes a log to file in every 2 secs,Image devopsdockeruh/simple-web-service creates a timestamp every two seconds to /usr/src/app/text.log
 Start the container with a bind mount to this file so that the logs are created into your filesystem
```
1. create a text.log file in local folder
$ touch text.log
2 create container with  text.log file mapped 
$ docker run  -v "$(pwd)/text.log:/usr/src/app/text.log" devopsdockeruh/simple-web-service
```
---
## Bind Mount
A Bind Mount maps a specific, user-defined file or directory from your host machine directly into the container.
- Host Dependency: Unlike volumes (where Docker controls the storage location), a bind mount relies on the exact directory structure of the host machine (
- Access Control: Any process on the host machine can modify the files in a bind mount at any time, which can sometimes lead to permission issues or security risks. 
