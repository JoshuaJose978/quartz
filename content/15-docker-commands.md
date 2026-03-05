---
title: Useful Docker Commands
---


To manage Docker containers and images, you can use the following commands. These commands will help you stop all running containers, remove them, and delete all Docker images.

### Stop all running containers

1. **Stop all containers**:
   ```bash
   docker stop $(docker ps -q)
   ```

   - `docker ps -q`: Lists the IDs of all running containers.
   - `docker stop`: Stops the containers based on their IDs.

### Remove all containers

2. **Remove all containers**:
   ```bash
   docker rm $(docker ps -a -q)
   ```

   - `docker ps -a -q`: Lists the IDs of all containers, both running and stopped.
   - `docker rm`: Removes the containers based on their IDs.

### Remove all Docker images

3. **Remove all images**:
   ```bash
   docker rmi $(docker images -q)
   ```

   - `docker images -q`: Lists the IDs of all Docker images.
   - `docker rmi`: Removes the images based on their IDs.

### Important Considerations

- **Network and Volumes**: If you also want to clean up networks and volumes, use the following commands:
  
  - **Remove all unused networks**:
    ```bash
    docker network prune -f
    ```

  - **Remove all unused volumes**:
    ```bash
    docker volume prune -f
    ```

- **Data Loss**: These operations are destructive and will remove all containers and images, including any persistent data stored in volumes not handled appropriately. Make sure to back up any important data before executing these commands.

These commands should be executed in a terminal or command prompt where Docker is installed and running. Always double-check which resources are being removed to avoid accidental data loss.
