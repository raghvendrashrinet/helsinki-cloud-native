# Ping Pong & Log Output App on Kubernetes

## Overview
This project demonstrates a small two-app system deployed on Kubernetes:

- The Ping Pong app handles requests to `/pingpong` and notifies the Log Output app.
- The Log Output app shows the latest generated log, the current ping count, and now also reads configuration from a ConfigMap.

## Current application behavior

### Ping Pong app
- Endpoint `/` returns a simple welcome message and the current pong count.
- Endpoint `/pingpong` increments the internal counter and sends a request to the Log Output app’s `/pings` endpoint.

### Log Output app
- Endpoint `/` returns:
  - the latest generated log entry
  - the current ping count
  - the content of a mounted file from a ConfigMap
  - the value of an environment variable from a ConfigMap
- Endpoint `/pings` increments the ping count when called by the Ping Pong app.

## ConfigMap-based configuration
The Log Output application now reads configuration from a ConfigMap.

The ConfigMap provides:
- one environment variable: `MESSAGE=hello world`
- one file: `information.txt` with the content `this text is from file`

The application then:
- reads the environment variable using Python `os.environ.get("MESSAGE")`
- reads the mounted file from `/data/information.txt`
- includes both values in the response

### Example output from `/`
```text
file content: this text is from file
env variable: MESSAGE=hello world
2026-05-18T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
Ping / Pongs: 3
```

## Kubernetes resources

### Deployments
- `pingpong-deployment` → runs the Ping Pong Flask app
- `logoutput-deployment` → runs the Log Output Flask app

### Services
- `pingpong-svc` → ClusterIP service for the Ping Pong app on port `2345`
- `logoutput-svc` → ClusterIP service for the Log Output app on port `2345`

### Ingress
- `/` → routes to the Log Output app
- `/pingpong` → routes to the Ping Pong app

## Request flow
1. The browser calls `/` or `/pingpong`.
2. The Ping Pong app increases its counter and notifies the Log Output app via `/pings`.
3. The Log Output app updates its own ping count and returns the latest values.

## Notes
This setup demonstrates how Kubernetes ConfigMaps can be used to inject:
- configuration values as environment variables
- files as mounted volumes

That makes the application more flexible without rebuilding the container image for small changes.
