## Reverse Proxy & Edge Layer (Nginx TLS + App)
A production pattern where Nginx acts as the single gateway handling SSL termination and static asset serving, mapping traffic directly to your upstream container.
```yaml
version: '3.8'

networks:
  proxy-net:

services:
  reverse-proxy:
    image: nginx:1.25-alpine
    container_name: nginx_edge
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro # SSL certificates path
    networks:
      - proxy-net
    depends_on:
      - app-server

  app-server:
    image: my-registry.com/team/app:v1.2.0
    container_name: production_app
    restart: unless-stopped
    expose:
      - "8080" # Exposes port to internal networks ONLY, not host ports
    networks:
      - proxy-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m" # Prevents containers from filling up host storage with endless log files
        max-file: "3"
```
