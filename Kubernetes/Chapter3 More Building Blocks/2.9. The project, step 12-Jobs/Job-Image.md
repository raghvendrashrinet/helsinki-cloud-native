## Kubernetes job best practices Docker image

Building a Docker image containing your script is the standard and recommended practice for running jobs in Kubernetes, rather than trying to mount or invoke a local script file directly. 

#### Why Building an Image is Best Practice
In Kubernetes, containers are designed to be immutable artifacts.  The cluster does not have access to your local file system; it only runs what is packaged inside the container image. 

- Immutability & Consistency: By baking the script into the image, you ensure that the exact same code tested in your CI pipeline is what runs in production. This eliminates "it works on my machine" issues.
- Version Control: Images can be tagged (e.g., with a Git commit SHA), allowing you to track exactly which version of the script is running and easily roll back if necessary. 
- Simplicity: It avoids complex workarounds like mounting ConfigMaps or dealing with file permission issues that arise when trying to execute external scripts inside a generic base image (like busybox). 

#### How to Implement This
The standard workflow involves two steps:

- 1. Create a *Dockerfile*: Use a base image (like alpine or bash) and copy your script into it using the COPY instruction.also make the script executable and set it as the entry point or command. 
```Dockerfile
# Use a lightweight base image
FROM alpine:latest

# Install bash if your script requires it (alpine uses sh by default)
RUN apk add --no-cache bash

# Copy your local script into the image
COPY run.sh /run.sh

# Make the script executable
RUN chmod +x /run.sh

# Define the command to run when the container starts
CMD ["/run.sh"]
```
- 2. *Build and Push*: Build this image in your CI pipeline and push it to a container registry (like Docker Hub, AWS ECR, or Google GCR). Your Kubernetes Job manifest will then simply reference this image. 

#### Job referencing the Image
```Yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: my-script-job
spec:
  template:
    spec:
      containers:
      - name: script-runner
        image: my-registry/my-script-image:v1.0  # Reference the built image
        # No need for complex command overrides if CMD is set in Dockerfile
      restartPolicy: OnFailure
```