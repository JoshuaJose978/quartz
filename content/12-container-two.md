---
title: Docker Fundamentals - Chapter 2
slug: docker-2
created: 2025-07-06
---

# Docker in Detail: CLI, Dockerfiles, and Docker Compose

## 1. Docker Architecture Overview

Before diving into commands and tools, let's understand Docker's core components:

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Host                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Docker Daemon (dockerd)             │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │    │
│  │  │ Images   │  │Containers│  │  Networks    │  │    │
│  │  └──────────┘  └──────────┘  └──────────────┘  │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │    │
│  │  │ Volumes  │  │   API    │  │Registry Client│  │    │
│  │  └──────────┘  └──────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                              ↑
                              │ REST API
                              ↓
┌─────────────────────────────────────────────────────────┐
│                    Docker Client                         │
│                   (docker command)                       │
└─────────────────────────────────────────────────────────┘
```

### Key Components:

- **Docker Client**: CLI tool that users interact with
- **Docker Daemon**: Background service managing Docker objects
- **Docker Registry**: Stores Docker images (Docker Hub, private registries)
- **Docker Objects**: Images, containers, networks, volumes

---

## 2. Essential Docker CLI Commands

### Image Management Commands

```bash
# Pull an image from registry
docker pull nginx:latest
docker pull ubuntu:22.04

# List all images
docker images
docker image ls

# Remove an image
docker rmi nginx:latest
docker image rm ubuntu:22.04

# Search for images
docker search redis

# View image details
docker image inspect nginx:latest

# Tag an image
docker tag nginx:latest myregistry/nginx:v1.0
```

### Container Lifecycle Commands

```bash
# Create and run a container
docker run nginx
docker run -d nginx                    # Run in detached mode
docker run -it ubuntu bash              # Interactive with TTY
docker run --name webserver nginx       # Named container
docker run -p 8080:80 nginx            # Port mapping
docker run -v /host/path:/container/path nginx  # Volume mount

# List containers
docker ps                              # Running containers
docker ps -a                           # All containers

# Start/Stop/Restart containers
docker start container_name
docker stop container_name
docker restart container_name

# Remove containers
docker rm container_name
docker rm -f container_name            # Force remove running container

# Execute commands in running container
docker exec -it container_name bash
docker exec container_name ls /app
```

### Container Inspection and Logs

```bash
# View container logs
docker logs container_name
docker logs -f container_name          # Follow log output
docker logs --tail 50 container_name   # Last 50 lines

# Inspect container details
docker inspect container_name

# View container processes
docker top container_name

# View resource usage
docker stats
docker stats container_name

# View container changes
docker diff container_name

# Copy files to/from container
docker cp file.txt container_name:/path/
docker cp container_name:/path/file.txt .
```

### Network Commands

```bash
# List networks
docker network ls

# Create network
docker network create mynetwork
docker network create --driver bridge --subnet 172.20.0.0/16 custom_network

# Connect/disconnect container to network
docker network connect mynetwork container_name
docker network disconnect mynetwork container_name

# Inspect network
docker network inspect bridge

# Remove network
docker network rm mynetwork
```

### Volume Commands

```bash
# Create volume
docker volume create myvolume

# List volumes
docker volume ls

# Inspect volume
docker volume inspect myvolume

# Remove volume
docker volume rm myvolume

# Remove all unused volumes
docker volume prune
```

### System Management Commands

```bash
# View Docker system info
docker info
docker version

# View disk usage
docker system df

# Clean up resources
docker system prune                    # Remove all unused data
docker system prune -a                 # Remove all unused data including images
docker container prune                 # Remove stopped containers
docker image prune                     # Remove unused images
docker network prune                   # Remove unused networks
```

---

## 3. Dockerfile: Building Custom Images

A Dockerfile is a text file containing instructions to build a Docker image.

### Dockerfile Instructions

```dockerfile
# Basic Dockerfile structure
FROM base_image:tag
WORKDIR /path/to/workdir
COPY source destination
RUN command
EXPOSE port
CMD ["executable", "param1", "param2"]
```

### Common Dockerfile Instructions

|Instruction|Purpose|Example|
|---|---|---|
|FROM|Base image|`FROM node:16-alpine`|
|WORKDIR|Set working directory|`WORKDIR /app`|
|COPY|Copy files from host|`COPY package.json .`|
|ADD|Copy files (with URL/tar support)|`ADD app.tar.gz /app`|
|RUN|Execute commands during build|`RUN npm install`|
|ENV|Set environment variables|`ENV NODE_ENV=production`|
|EXPOSE|Document exposed ports|`EXPOSE 3000`|
|CMD|Default command|`CMD ["node", "app.js"]`|
|ENTRYPOINT|Configure container executable|`ENTRYPOINT ["docker-entrypoint.sh"]`|
|ARG|Build-time variables|`ARG VERSION=1.0`|
|LABEL|Add metadata|`LABEL maintainer="admin@example.com"`|
|USER|Set user for RUN/CMD/ENTRYPOINT|`USER node`|
|VOLUME|Create mount point|`VOLUME ["/data"]`|

### Example 1: Node.js Application Dockerfile

```dockerfile
# Use official Node.js runtime as base image
FROM node:16-alpine

# Set working directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application source
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /usr/src/app

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "server.js"]
```

### Example 2: Multi-stage Build for Go Application

```dockerfile
# Build stage
FROM golang:1.19-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Final stage
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/main .

# Expose port
EXPOSE 8080

# Run application
CMD ["./main"]
```

### Example 3: Python Flask Application

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Building and Using Docker Images

```bash
# Build image from Dockerfile
docker build -t myapp:latest .
docker build -t myapp:v1.0 -f Dockerfile.prod .
docker build --build-arg VERSION=1.0 -t myapp:1.0 .

# Push image to registry
docker tag myapp:latest myregistry/myapp:latest
docker push myregistry/myapp:latest

# Save/Load images
docker save -o myapp.tar myapp:latest
docker load -i myapp.tar
```

---

## 4. Docker Compose: Multi-Container Applications

Docker Compose is a tool for defining and running multi-container Docker applications using a YAML file.

### Docker Compose File Structure

```yaml
version: '3.8'

services:
  service_name:
    image: image_name:tag
    build: ./path
    ports:
      - "host:container"
    volumes:
      - ./host/path:/container/path
    environment:
      - ENV_VAR=value
    depends_on:
      - other_service

volumes:
  volume_name:

networks:
  network_name:
```

### Example 1: WordPress with MySQL

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: somewordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
    networks:
      - wp_network

  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    ports:
      - "8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - wp_network

volumes:
  db_data:
  wordpress_data:

networks:
  wp_network:
    driver: bridge
```

### Example 2: Microservices Application

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - backend
    networks:
      - app_network

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - app_network

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    networks:
      - app_network

volumes:
  postgres_data:
  redis_data:

networks:
  app_network:
    driver: bridge
```

### Example 3: Development Environment

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    command: npm run dev
    depends_on:
      - mongodb
      - mailhog

  mongodb:
    image: mongo:5.0
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
      - MONGO_INITDB_DATABASE=devdb
    ports:
      - "27017:27017"

  mongo-express:
    image: mongo-express
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_ADMINUSERNAME=admin
      - ME_CONFIG_MONGODB_ADMINPASSWORD=password
      - ME_CONFIG_MONGODB_SERVER=mongodb
    depends_on:
      - mongodb

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI

volumes:
  mongo_data:
```

### Docker Compose Commands

```bash
# Start services
docker-compose up
docker-compose up -d                   # Detached mode
docker-compose up --build              # Rebuild images

# Stop services
docker-compose down
docker-compose down -v                 # Remove volumes
docker-compose stop                    # Stop without removing

# View services
docker-compose ps
docker-compose logs
docker-compose logs -f service_name

# Execute commands
docker-compose exec service_name bash
docker-compose run service_name command

# Scale services
docker-compose up -d --scale web=3

# Build images
docker-compose build
docker-compose build --no-cache

# Pull images
docker-compose pull

# Validate compose file
docker-compose config
```

### Advanced Docker Compose Features

#### Override Files

```yaml
# docker-compose.yml (base)
version: '3.8'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"

# docker-compose.override.yml (development)
version: '3.8'
services:
  web:
    build: .
    volumes:
      - .:/app
    environment:
      - DEBUG=true
    ports:
      - "8080:80"
```

#### Using .env Files

```bash
# .env file
POSTGRES_VERSION=14
APP_PORT=3000
DB_PASSWORD=secret
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:${POSTGRES_VERSION}
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
  
  app:
    build: .
    ports:
      - "${APP_PORT}:3000"
```

---

## 5. Best Practices

### Dockerfile Best Practices

1. **Use specific base image tags**
    
    ```dockerfile
    # Good
    FROM node:16.14-alpine
    
    # Bad
    FROM node:latest
    ```
    
2. **Minimize layers**
    
    ```dockerfile
    # Good
    RUN apt-get update && apt-get install -y \
        package1 \
        package2 \
        && rm -rf /var/lib/apt/lists/*
    
    # Bad
    RUN apt-get update
    RUN apt-get install -y package1
    RUN apt-get install -y package2
    ```
    
3. **Use .dockerignore**
    
    ```
    node_modules
    npm-debug.log
    .git
    .env
    .DS_Store
    *.md
    .gitignore
    ```
    
4. **Run as non-root user**
    
    ```dockerfile
    RUN groupadd -r appuser && useradd -r -g appuser appuser
    USER appuser
    ```
    
5. **Use multi-stage builds**
    
    ```dockerfile
    FROM node:16 AS builder
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci
    COPY . .
    RUN npm run build
    
    FROM node:16-alpine
    WORKDIR /app
    COPY --from=builder /app/dist ./dist
    COPY package*.json ./
    RUN npm ci --production
    CMD ["node", "dist/index.js"]
    ```
    

### Docker Compose Best Practices

1. **Use explicit service dependencies**
    
    ```yaml
    depends_on:
      - db
      - redis
    ```
    
2. **Set resource limits**
    
    ```yaml
    services:
      web:
        deploy:
          resources:
            limits:
              cpus: '0.5'
              memory: 512M
    ```
    
3. **Use named volumes**
    
    ```yaml
    volumes:
      - db_data:/var/lib/postgresql/data  # Good
      - ./data:/var/lib/postgresql/data    # Less portable
    ```
    
4. **Separate environments**
    
    ```bash
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
    ```
    

---

## 6. Chapter Summary

In this chapter, we've covered the practical aspects of working with Docker:

1. **Docker CLI Commands**: Essential commands for managing images, containers, networks, and volumes. These commands form the foundation of Docker operations.
    
2. **Dockerfiles**: The blueprint for creating custom Docker images. We learned about various instructions and best practices for writing efficient, secure Dockerfiles.
    
3. **Docker Compose**: A powerful tool for defining and managing multi-container applications. Perfect for development environments and deploying related services together.
    

Key takeaways:

- Master the basic Docker CLI commands before moving to advanced topics
- Write Dockerfiles that are efficient, secure, and maintainable
- Use Docker Compose for applications requiring multiple services
- Follow best practices to avoid common pitfalls
- Always consider security (non-root users, minimal base images)

### Hands-on Exercises:

1. Create a Dockerfile for your favorite programming language application
2. Build a multi-container application with Docker Compose (web app + database)
3. Practice using volumes for data persistence
4. Implement a multi-stage build to reduce image size
5. Set up a development environment using Docker Compose with hot-reloading

### Next Steps:

- Chapter 3: Container Orchestration with Docker Swarm
- Chapter 4: Introduction to Kubernetes
- Chapter 5: CI/CD with Docker
- Chapter 6: Security Best Practices
