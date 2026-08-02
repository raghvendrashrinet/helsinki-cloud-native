# Loki Log Storage in Production

This document explains how logs are sent, ingested, and persisted in Loki for a production-style Kubernetes observability stack.

## 1. Purpose

In production, Loki serves as the centralized log engine. Application and cluster logs are collected by a shipper, sent to Loki over HTTP, and stored in Loki's configured backend.

This repository uses `k8smon` (Grafana Alloy / k8s-monitoring) to collect pod logs and push them to Loki.

`k8smon` is the Kubernetes log collection agent: it tails pod log files from nodes, labels them, and forwards them to Loki.

## 2. Key components

- `k8smon` / Alloy
  - A log collector that tails Kubernetes pod log files from the node filesystem.
  - Adds Kubernetes metadata labels such as `namespace`, `pod`, `container`, and `job`.
  - Sends logs to a Loki destination using the Loki push API.

- `Loki`
  - Receives log streams and indexes them.
  - Stores logs in its chunk storage backend.
  - Exposes query endpoints for Grafana and log exploration.

- `Grafana`
  - Visualizes logs via Loki.
  - Uses LogQL to query stored log streams.

## 3. How logs flow in production

1. A pod writes stdout/stderr logs to the node filesystem under `/var/log/pods/...`.
2. `k8smon` runs as a collector on cluster nodes and tails those files.
3. `k8smon` packages logs into Loki push requests.
4. `k8smon` sends requests to the Loki push endpoint.
5. Loki receives the request and stores logs into its backend.
6. Grafana queries Loki to display logs.

## 4. The Loki push endpoint

In the `k8smon` values file, this destination is defined:

```yaml
destinations:
  localLoki:
    type: loki
    url: http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push
    tenantId: "1"
```

### What this means

- `type: loki`
  - The destination is a Loki-compatible log ingestion target.
- `url: http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push`
  - This is the internal Kubernetes service URL for Loki.
  - `loki-gateway` is the service name.
  - `monitoring` is the namespace.
  - `svc.cluster.local` is the Kubernetes cluster DNS suffix.
  - `/loki/api/v1/push` is Loki's HTTP ingestion API.
- `tenantId: "1"`
  - Sets a tenant or organization identifier.
  - Loki can use this value to separate log data if multi-tenancy is enabled.

## 5. Internal Kubernetes routing

The URL resolves within the cluster, not from the public internet.

```
[k8smon pod] --> [Service: loki-gateway in namespace monitoring] --> [Loki pods]
```

The service name and namespace form the internal DNS name:

```
loki-gateway.monitoring.svc.cluster.local
```

This means `k8smon` reaches Loki through the cluster service mesh and Kubernetes DNS.

## 6. What Loki stores

Loki does not store logs in the URL itself. The URL is only the ingestion endpoint.

After ingestion:

- Loki parses the push request.
- Loki indexes labels and stores log stream chunks.
- The actual stored data depends on Loki's backend config.

### Typical production backends

Loki can persist data to several backends in production, including:

- object storage: AWS S3, GCS, Azure Blob Storage
- filesystem
- Cassandra
- DynamoDB (for index)

In production, object storage is the recommended backend for durability and scale.

## 7. Example Loki storage config

A production-ready Loki config will often include:

```yaml
loki:
  commonConfig:
    replication_factor: 3
  storage:
    type: s3
    s3:
      endpoint: s3.amazonaws.com
      bucketnames: loki-logs-prod
      access_key_id: <REDACTED>
      secret_access_key: <REDACTED>
```

For local testing or low-scale environments, filesystem storage is acceptable, but it is not ideal for production.

## 8. How Grafana queries logs

Grafana uses Loki as a datasource to query logs with LogQL.

Example query:

```logql
{namespace="default"} |= "error"
```

Grafana can also link logs to metrics and support alerts based on log patterns.

## 9. Verification in production

Check the pipeline with:

- `kubectl get pods -n monitoring`
- `kubectl get svc -n monitoring`
- Loki push metrics such as `loki_distributor_bytes_received_total`
- Grafana Explore queries for log streams

## 10. Summary

- `k8smon` collects pod logs and pushes them to Loki.
- The URL `http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push` is the internal Loki ingestion endpoint.
- Loki stores the logs in its configured backend, not at the URL itself.
- In production, use a durable backend like object storage for Loki.
