### Docker Compose
##### docker-compose.yaml
```yaml
services:
  yt-dlp-ubuntu:
    image: <username>/<repositoryname>  
    build: .
```
Dockerfile example :
```Dockerfile
FROM ubuntu:24.04

WORKDIR /mydir

RUN apt-get update && apt-get install -y curl python3 ffmpeg
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
RUN chmod a+x /usr/local/bin/yt-dlp

ENTRYPOINT ["/usr/local/bin/yt-dlp"]
```
Build and Push
```bash
$ docker compose build
$ docker compose push
```

#### Volumes in Docker Compose
```yaml
services:
  yt-dlp-ubuntu:
    image: <username>/<repositoryname>
    build: .
    volumes:
      - .:/mydir
    container_name: yt-dlp
    #can also give the container a name
```
Run Container `$ docker compose run yt-dlp-ubuntu https://www.youtube.com/watch?v=saEpkcVi1d4`
`$ docker compose run yt-dlp-ubuntu https://www.youtube.com/watch?v=saEpkcVi1d4`

#### docker-compose.yaml file to define two containers
```yaml
services:
  nginx:
    image: nginx:1.29
  database:
    image: postgres:18
```
`docker compose up`
