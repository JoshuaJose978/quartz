---
title: Docker Fundamentals - Chapter 3
slug: docker-3
created: 2025-07-06
---
# Container Orchestration with Docker Swarm

## 1. Introduction to Container Orchestration

Container orchestration automates the deployment, management, scaling, and networking of containers. While Docker Compose is great for single-host deployments, production environments need more robust solutions.

### Why Container Orchestration?

```
Single Host (Docker Compose)         Multi-Host (Docker Swarm)
┌─────────────────────┐             ┌─────────────────────┐
│   Docker Host       │             │   Manager Node 1    │
│  ┌────┐ ┌────┐     │             │  ┌──────────────┐   │
│  │App1│ │App2│     │             │  │Swarm Manager │   │
│  └────┘ └────┘     │             │  └──────────────┘   │
│  ┌────┐ ┌────┐     │             └─────────────────────┘
│  │DB  │ │Cache│    │             ┌─────────────────────┐
│  └────┘ └────┘     │             │   Worker Node 1     │
└─────────────────────┘             │  ┌────┐ ┌────┐     │
                                    │  │App1│ │App2│     │
Limited to one host                 │  └────┘ └────┘     │
Manual scaling                      └─────────────────────┘
No automatic failover               ┌─────────────────────┐
                                    │   Worker Node 2     │
                                    │  ┌────┐ ┌────┐     │
                                    │  │App1│ │DB  │     │
                                    │  └────┘ └────┘     │
                                    └─────────────────────┘
```

### Key Benefits of Orchestration:

- **High Availability**: Automatic failover when nodes fail
- **Scalability**: Easy horizontal scaling across multiple nodes
- **Load Balancing**: Distribute traffic across container instances
- **Rolling Updates**: Zero-downtime deployments
- **Self-Healing**: Automatic container restart and rescheduling
- **Service Discovery**: Built-in DNS for service communication

---

## 2. Docker Swarm Architecture

Docker Swarm is Docker's native clustering and orchestration solution, turning multiple Docker hosts into a single virtual host.

### Swarm Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Swarm Cluster                     │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Manager Node   │  │  Manager Node   │   Leader Election │
│  │   (Leader)      │  │   (Follower)    │   via Raft       │
│  │  ┌───────────┐  │  │  ┌───────────┐  │                  │
│  │  │   etcd    │  │  │  │   etcd    │  │   Distributed    │
│  │  │  (state)  │  │  │  │  (state)  │  │   State Store    │
│  │  └───────────┘  │  │  └───────────┘  │                  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │                  │
│  │  │ Scheduler │  │  │  │ Scheduler │  │                  │
│  │  └───────────┘  │  │  └───────────┘  │                  │
│  └────────┬────────┘  └─────────────────┘                  │
│           │                                                  │
│           │ Task Assignment                                  │
│           ↓                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Worker Node 1  │  │  Worker Node 2  │                  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │                  │
│  │  │Container 1│  │  │  │Container 3│  │   Service Tasks  │
│  │  └───────────┘  │  │  └───────────┘  │                  │
│  │  ┌───────────┐  │  │  ┌───────────┐  │                  │
│  │  │Container 2│  │  │  │Container 4│  │                  │
│  │  └───────────┘  │  │  └───────────┘  │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                              │
│  Overlay Network (Service Communication)                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts:

1. **Nodes**:
    
    - **Manager Nodes**: Handle cluster management, scheduling, and orchestration
    - **Worker Nodes**: Execute containers (tasks)
    - Manager nodes can also run workloads
2. **Services**:
    
    - Declarative model for running applications
    - Defines desired state (replicas, image, ports, etc.)
    - Two types: replicated (multiple instances) and global (one per node)
3. **Tasks**:
    
    - Atomic unit of scheduling
    - One task = one container
    - Assigned to nodes by the scheduler
4. **Raft Consensus**:
    
    - Managers use Raft for distributed state management
    - Requires odd number of managers (3, 5, 7)
    - Maintains consistency across the cluster

---

## 3. Setting Up a Docker Swarm Cluster

### Prerequisites

- Multiple Docker hosts (VMs or physical machines)
- Docker Engine 1.12.0 or higher
- Ports 2377 (cluster management), 7946 (node communication), 4789 (overlay network)

### Initialize Swarm on First Manager

```bash
# Initialize swarm on the first manager node
docker swarm init --advertise-addr <MANAGER-IP>

# Example output:
# Swarm initialized: current node (abcd1234) is now a manager.
# 
# To add a worker to this swarm, run the following command:
#     docker swarm join --token SWMTKN-1-abc...xyz 192.168.1.100:2377
# 
# To add a manager to this swarm, run 'docker swarm join-token manager'
```

### Join Nodes to Swarm

```bash
# Get join token for workers
docker swarm join-token worker

# Get join token for managers
docker swarm join-token manager

# Join a worker node
docker swarm join --token SWMTKN-1-abc...xyz 192.168.1.100:2377

# Join additional manager node
docker swarm join --token SWMTKN-1-manager...xyz 192.168.1.100:2377

# View all nodes
docker node ls
```

### Node Management

```bash
# Promote worker to manager
docker node promote node-name

# Demote manager to worker
docker node demote node-name

# Update node availability
docker node update --availability drain node-name
docker node update --availability active node-name
docker node update --availability pause node-name

# Add labels to nodes
docker node update --label-add type=gpu node-name
docker node update --label-add zone=us-east node-name

# Remove node from swarm (run on the node)
docker swarm leave
docker swarm leave --force  # For managers

# Remove node from swarm (run on manager)
docker node rm node-name
```

---

## 4. Deploying Services in Swarm

### Creating Services

```bash
# Create a basic service
docker service create --name web nginx

# Create service with replicas
docker service create --name web --replicas 3 nginx

# Create service with published port
docker service create --name web --replicas 3 -p 80:80 nginx

# Create service with environment variables
docker service create --name api \
  --replicas 3 \
  --env DB_HOST=db.example.com \
  --env DB_PORT=5432 \
  myapp:latest

# Create service with resource limits
docker service create --name web \
  --replicas 3 \
  --limit-cpu 0.5 \
  --limit-memory 512M \
  --reserve-cpu 0.25 \
  --reserve-memory 256M \
  nginx

# Create service with custom network
docker service create --name web \
  --network myoverlay \
  --replicas 3 \
  nginx
```

### Service Templates with Stack Deploy

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.role == worker
          - node.labels.zone == us-east
    ports:
      - "80:80"
    networks:
      - webnet
    volumes:
      - web_data:/usr/share/nginx/html

  api:
    image: myapp:latest
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    environment:
      - DB_HOST=db
      - REDIS_HOST=redis
    networks:
      - webnet
      - backend
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    deploy:
      placement:
        constraints:
          - node.labels.type == database
      replicas: 1
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - backend

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
    networks:
      - backend

networks:
  webnet:
    driver: overlay
  backend:
    driver: overlay
    internal: true

volumes:
  web_data:
    driver: local
  db_data:
    driver: local

secrets:
  db_password:
    external: true
```

Deploy the stack:

```bash
# Deploy stack
docker stack deploy -c docker-compose.yml myapp

# List stacks
docker stack ls

# List stack services
docker stack services myapp

# List stack tasks
docker stack ps myapp

# Remove stack
docker stack rm myapp
```

### Managing Services

```bash
# List all services
docker service ls

# Inspect service
docker service inspect web
docker service inspect --pretty web

# View service logs
docker service logs web
docker service logs -f web
docker service logs --tail 50 web

# List service tasks
docker service ps web

# Update service image
docker service update --image nginx:latest web

# Update service replicas
docker service scale web=5
docker service update --replicas 5 web

# Update service configuration
docker service update \
  --env-add NEW_VAR=value \
  --env-rm OLD_VAR \
  --publish-add 443:443 \
  web

# Remove service
docker service rm web
```

---

## 5. Scaling and Load Balancing

### Horizontal Scaling

```bash
# Scale single service
docker service scale web=10

# Scale multiple services
docker service scale web=10 api=5 worker=3

# Scale with update config
docker service update \
  --replicas 10 \
  --update-parallelism 2 \
  --update-delay 30s \
  web
```

### Load Balancing

Docker Swarm includes two types of load balancing:

#### 1. Internal Load Balancing (Service Discovery)

```
┌─────────────────────────────────────────┐
│            Overlay Network               │
│                                          │
│   ┌─────────┐     VIP: 10.0.0.5         │
│   │   API   │ ─────────┐                │
│   │ Service │          │                │
│   └─────────┘          ↓                │
│                   ┌──────────┐           │
│                   │ IPVS LB  │           │
│                   └──────────┘           │
│                    ↙    ↓    ↘           │
│            ┌────┐   ┌────┐   ┌────┐     │
│            │Task│   │Task│   │Task│     │
│            │ 1  │   │ 2  │   │ 3  │     │
│            └────┘   └────┘   └────┘     │
└─────────────────────────────────────────┘
```

#### 2. External Load Balancing (Ingress Routing Mesh)

```
                     External Traffic
                           │
                           ↓
┌─────────────────────────────────────────────┐
│              Ingress Network                 │
│                                              │
│  Node 1:80     Node 2:80      Node 3:80     │
│      ↓             ↓              ↓          │
│  ┌────────┐   ┌────────┐    ┌────────┐     │
│  │ Routing│   │ Routing│    │ Routing│     │
│  │  Mesh  │   │  Mesh  │    │  Mesh  │     │
│  └────────┘   └────────┘    └────────┘     │
│       ↘           ↓            ↙             │
│         ↘         ↓          ↙               │
│           ┌──────────────┐                   │
│           │  Service VIP │                   │
│           └──────────────┘                   │
│            ↙      ↓      ↘                   │
│      Task 1    Task 2    Task 3              │
│     (Node 2)  (Node 1)  (Node 3)             │
└─────────────────────────────────────────────┘
```

### Configure Load Balancing

```yaml
version: '3.8'

services:
  web:
    image: nginx
    deploy:
      replicas: 3
      endpoint_mode: vip  # Virtual IP (default)
      # endpoint_mode: dnsrr  # DNS round-robin
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: ingress  # Routing mesh (default)
        # mode: host   # Direct host port binding
```

---

## 6. Managing Secrets and Configs

### Docker Secrets

```bash
# Create secrets
echo "mypassword" | docker secret create db_password -
docker secret create ssh_key ~/.ssh/id_rsa

# List secrets
docker secret ls

# Inspect secret metadata
docker secret inspect db_password

# Use secrets in services
docker service create --name db \
  --secret db_password \
  --env POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres

# Update service with new secret
docker service update \
  --secret-rm old_secret \
  --secret-add source=new_secret,target=secret_file \
  myservice

# Remove secret
docker secret rm db_password
```

### Docker Configs

```bash
# Create config from file
docker config create nginx_conf ./nginx.conf

# Create config from stdin
echo "server { listen 80; }" | docker config create nginx_basic -

# List configs
docker config ls

# Use configs in services
docker service create --name web \
  --config source=nginx_conf,target=/etc/nginx/nginx.conf \
  nginx

# Update service config
docker service update \
  --config-rm old_config \
  --config-add source=new_config,target=/etc/app/config.json \
  myservice
```

### Example: WordPress with Secrets

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    deploy:
      replicas: 3
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    networks:
      - wordpress_net

  db:
    image: mysql:8.0
    deploy:
      placement:
        constraints:
          - node.role == manager
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD_FILE: /run/secrets/db_password
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets:
      - db_password
      - db_root_password
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - wordpress_net

networks:
  wordpress_net:
    driver: overlay

volumes:
  db_data:

secrets:
  db_password:
    external: true
  db_root_password:
    external: true
```

---

## 7. Swarm Networking

### Network Types in Swarm

1. **Overlay Networks**: Multi-host networks for service communication
2. **Ingress Network**: Special overlay for routing mesh
3. **Bridge Networks**: Single-host networks (limited use in Swarm)

### Creating and Managing Networks

```bash
# Create overlay network
docker network create --driver overlay myapp_net

# Create encrypted overlay network
docker network create --driver overlay --opt encrypted secure_net

# Create overlay with custom subnet
docker network create --driver overlay \
  --subnet 10.10.0.0/16 \
  --gateway 10.10.0.1 \
  custom_net

# Create attachable overlay (for standalone containers)
docker network create --driver overlay --attachable mixed_net

# List networks
docker network ls

# Inspect network
docker network inspect myapp_net
```

### Network Architecture

```
┌─────────────────────────────────────────────────┐
│                  Manager Node                    │
│  ┌────────────────────────────────────────┐     │
│  │         Network Control Plane           │     │
│  │  (Network creation, IP allocation)      │     │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────┐
│              Overlay Network (VXLAN)             │
│                                                  │
│  Node 1              Node 2              Node 3  │
│  ┌─────┐            ┌─────┐            ┌─────┐  │
│  │ br0 │            │ br0 │            │ br0 │  │
│  └──┬──┘            └──┬──┘            └──┬──┘  │
│     │                  │                  │      │
│  ┌──┴──┐ ┌──────┐  ┌──┴──┐ ┌──────┐  ┌──┴──┐  │
│  │Web:1│ │API:1 │  │Web:2│ │DB:1  │  │API:2│  │
│  │10.0.│ │10.0. │  │10.0.│ │10.0. │  │10.0.│  │
│  │0.5  │ │0.10  │  │0.6  │ │0.20  │  │0.11 │  │
│  └─────┘ └──────┘  └─────┘ └──────┘  └─────┘  │
└─────────────────────────────────────────────────┘
```

### Service Discovery

```bash
# Services can discover each other by name
docker service create --name web --network myapp_net nginx
docker service create --name api --network myapp_net myapi

# Inside api container:
# ping web  # Works!
# nslookup web  # Returns VIP

# Custom aliases
docker service create --name database \
  --network myapp_net \
  --network-alias db \
  --network-alias postgres \
  postgres
```

---

## 8. High Availability and Fault Tolerance

### Manager High Availability

```
Fault Tolerance by Manager Count:
┌─────────────┬──────────────┬─────────────────┐
│  Managers   │ Quorum Size  │ Fault Tolerance │
├─────────────┼──────────────┼─────────────────┤
│      1      │      1       │        0        │
│      3      │      2       │        1        │
│      5      │      3       │        2        │
│      7      │      4       │        3        │
└─────────────┴──────────────┴─────────────────┘
```

### Implementing HA

```bash
# Distribute managers across availability zones
docker node update --label-add zone=us-east-1a manager1
docker node update --label-add zone=us-east-1b manager2
docker node update --label-add zone=us-east-1c manager3

# Service with HA constraints
docker service create --name critical-app \
  --replicas 6 \
  --constraint 'node.labels.zone != node.labels.zone' \
  --update-failure-action rollback \
  --update-max-failure-ratio 0.2 \
  myapp:latest
```

### Health Checks

```yaml
version: '3.8'

services:
  web:
    image: myapp:latest
    deploy:
      replicas: 3
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Rolling Updates with Rollback

```bash
# Update with automatic rollback
docker service update \
  --image myapp:v2 \
  --update-parallelism 1 \
  --update-delay 30s \
  --update-failure-action rollback \
  --update-monitor 5m \
  --update-max-failure-ratio 0.2 \
  web

# Manual rollback
docker service rollback web

# Update with health check validation
docker service update \
  --image myapp:v2 \
  --update-order start-first \
  --health-cmd "curl -f http://localhost/health" \
  --health-interval 10s \
  --health-retries 3 \
  web
```

### Backup Swarm Configuration

```bash
# Backup Swarm (on manager)
# 1. Stop Docker
systemctl stop docker

# 2. Backup Swarm directory
tar -czvf swarm-backup.tar.gz /var/lib/docker/swarm/

# 3. Start Docker
systemctl start docker

# Disaster Recovery Process:
# 1. Restore /var/lib/docker/swarm/ on a manager
# 2. Force new cluster
docker swarm init --force-new-cluster --advertise-addr <NODE-IP>

# 3. Re-add other nodes
```

---

## 9. Monitoring and Maintenance

### Built-in Monitoring Commands

```bash
# Monitor service health
watch docker service ls
watch docker service ps web

# View service logs across all nodes
docker service logs -f web
docker service logs --since 1h web

# Node resource usage
docker node ps $(docker node ls -q)

# Detailed task information
docker inspect <task-id>
```

### Prometheus + Grafana Stack Example

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    deploy:
      placement:
        constraints:
          - node.role == manager
    volumes:
      - prometheus_data:/prometheus
    configs:
      - source: prometheus_config
        target: /etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter
    deploy:
      mode: global
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor
    deploy:
      mode: global
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - monitoring

  grafana:
    image: grafana/grafana
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
    secrets:
      - grafana_password
    networks:
      - monitoring

networks:
  monitoring:
    driver: overlay

volumes:
  prometheus_data:
  grafana_data:

configs:
  prometheus_config:
    file: ./prometheus.yml

secrets:
  grafana_password:
    external: true
```

### Maintenance Tasks

```bash
# Drain node for maintenance
docker node update --availability drain worker1

# Perform maintenance...

# Return node to active
docker node update --availability active worker1

# Clean up unused resources
docker system prune -a
docker volume prune
docker network prune

# Update Docker Engine (rolling)
# For each node:
# 1. Drain node
# 2. Update Docker
# 3. Rejoin swarm
# 4. Activate node
```

---

## 10. Chapter Summary

In this chapter, we explored Docker Swarm, Docker's native orchestration solution:

1. **Container Orchestration Fundamentals**: Understanding why orchestration is necessary for production deployments
    
2. **Swarm Architecture**: Manager/worker nodes, Raft consensus, and distributed state management
    
3. **Cluster Setup**: Initializing swarms and managing nodes
    
4. **Service Deployment**: Creating and managing services using both CLI and stack files
    
5. **Scaling and Load Balancing**: Horizontal scaling with built-in load balancing
    
6. **Secrets and Configs**: Secure management of sensitive data and configuration
    
7. **Networking**: Overlay networks and service discovery
    
8. **High Availability**: Implementing fault-tolerant deployments
    
9. **Monitoring**: Tools and strategies for swarm observability
    

### Key Takeaways:

- Docker Swarm provides production-ready orchestration with minimal complexity
- Built-in features include load balancing, service discovery, and rolling updates
- Raft consensus ensures consistent state across manager nodes
- Overlay networks enable secure multi-host communication
- Health checks and rollback capabilities ensure reliable deployments

### When to Use Docker Swarm:

✅ **Good for:**

- Teams already using Docker
- Simple to medium complexity deployments
- Quick setup and learning curve
- Built-in Docker integration

❌ **Consider alternatives when:**

- Need advanced scheduling features
- Require extensive third-party integrations
- Managing very large clusters (1000+ nodes)
- Need multi-cloud federation

### Practice Exercises:

1. Set up a 3-node Swarm cluster (1 manager, 2 workers)
2. Deploy a multi-service application using stack deploy
3. Implement rolling updates with health checks
4. Configure monitoring with Prometheus and Grafana
5. Practice disaster recovery scenarios

### Next Steps:

- Chapter 4: Introduction to Kubernetes
- Chapter 5: Swarm vs Kubernetes Comparison
- Chapter 6: Production Best Practices
