## Understanding Kubernetes `subPath` for Volume Mounts

When transitioning from Docker host volume mounts to Kubernetes volumes, a common trap is accidentally overwriting container application files. This document explains how the `subPath` property solves this issue.

### The Problem: Directory Overwriting
By default, when you mount a Kubernetes volume (like an `emptyDir`) to a path inside a container (e.g., `/app`), Kubernetes masks and completely hides the pre-existing contents of that directory. 

If your container image has code or dependencies built into `/app` (such as `app.py`), mounting a fresh, empty volume over `/app` causes the application to crash with a missing file error (`app.py not found`).

### The Solution: `subPath`
The `subPath` field allows you to isolate and mount **only a specific file or single subdirectory** from a volume into your container, leaving the rest of the target directory untouched.

```yaml
        volumeMounts:
        - name: myvol
          mountPath: /app/log.txt  # The precise destination path in the container
          subPath: log.txt         # Isolates just this file inside the emptyDir volume
