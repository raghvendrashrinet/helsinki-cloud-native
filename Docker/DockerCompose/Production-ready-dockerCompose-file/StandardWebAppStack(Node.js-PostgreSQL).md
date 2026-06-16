### The Standard Web App Stack (Node.js + PostgreSQL)
This setup separates the public-facing application from the private database using isolated networks, ensures the database is fully healthy before the app boots, and configures explicit resource limits.
```yaml
version: '3.8'

networks:
  frontend-net:
    driver: bridge
  backend-net:
    driver: bridge
    internal: true # Restricts this network from accessing the public internet

volumes:
  postgres_data:
    driver: local

services:
  web:
    image: node:20-alpine
    container_name: web_app_prod
    restart: unless-stopped
    environment:
      NODE_ENV: production
      DATABASE_URL: postgres://app_user:${DB_PASSWORD}@db:5432/app_db
      PORT: 3000
    ports:
      - "127.0.0.1:3000:3000" # Binds only to localhost for security behind a reverse proxy (Nginx)
    networks:
      - frontend-net
      - backend-net
    depends_on:
      db:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          memory: 256M

  db:
    image: postgres:16-alpine
    container_name: postgres_prod
    restart: unless-stopped
    user: postgres # Ensures process runs as non-root
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD} # Injected securely via .env file
      POSTGRES_DB: app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```
