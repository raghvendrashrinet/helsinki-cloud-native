## Microservices Stack (Python API + Redis Cache + Worker)
Commonly used for background processing or asynchronous task queues (like Celery/Redis setups). It reuses the same build context for different service responsibilities.
```yaml
version: '3.8'

networks:
  microservice-net:
    driver: bridge

volumes:
  redis_cache:

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: api_service
    restart: always
    command: gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
    environment:
      - REDIS_URL=redis://cache:6373/0
    ports:
      - "8000:8000"
    networks:
      - microservice-net
    depends_on:
      cache:
        condition: service_healthy

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: worker_service
    restart: always
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://cache:6373/0
    networks:
      - microservice-net
    depends_on:
      cache:
        condition: service_healthy

  cache:
    image: redis:7-alpine
    container_name: redis_prod
    command: redis-server --requirepass ${REDIS_PASSWORD} --port 6373
    volumes:
      - redis_cache:/data
    networks:
      - microservice-net
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "6373", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
```
