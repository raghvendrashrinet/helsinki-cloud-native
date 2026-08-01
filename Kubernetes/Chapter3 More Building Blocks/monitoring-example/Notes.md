


```
                  ┌────────────────────────┐
                  │        GRAFANA         │
                  │  (Unified Dashboards)  │
                  └───────────▲────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
      PromQL Queries                      LogQL Queries
            │                                   │
┌───────────┴───────────┐           ┌───────────┴───────────┐
│      PROMETHEUS       │           │         LOKI          │
│ (Metrics TSDB Engine) │           │ (Log Storage Engine)  │
└───────────▲───────────┘           └───────────▲───────────┘
            │ Scrapes                           │ Pushes Logs
            │ Metrics                           │
┌───────────┴───────────┐           ┌───────────┴───────────┐
│   EXPORTERS / PODS    │           │     GRAFANA ALLOY     │
│ (node-exporter, kms)  │           │   (k8s-monitoring)    │
└───────────────────────┘           └───────────▲───────────┘
                                                │ Tails stdout/stderr
                                                │ (/var/log/pods)
                                    ┌───────────┴───────────┐
                                    │     K8s Node Pods     │
                                    └───────────────────────┘
```


Production Observability & Architecture Blueprint1. System Architecture & Telemetry PipelineThis production architecture uses a dual-engine telemetry model in Grafana: Prometheus handles metrics via direct exporter scraping, while Grafana Alloy handles log tailing and ingestion into Loki. 

```
                               ┌─────────────────────────────────────────────────┐
                               │                 GRAFANA                         │
                               │  (Dashboards, Alerting, Cross-Linking UI)       │
                               └─────────▲──────────────▲──────────────▲─────────┘
                                         │              │              │
                                    PromQL            LogQL          TraceQL
                                         │              │              │
┌────────────────────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────┐
│ OBSERVABILITY BACKENDS                 │              │              │                                        │
│                               ┌────────┴────────┐ ┌───┴────┐ ┌───────┴────────┐                                │
│                               │   Prometheus    │ │  Loki  │ │     Tempo      │                               │
│                               │(Metrics Engine) │ │ (Logs) │ │(Tracing Engine)│                               │
│                               └────────▲────────┘ └───▲────┘ └───────▲────────┘                               │
│                                        │              │              │                                        │
└────────────────────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────┘───────┘
                                         │ Direct Scrape│ Push Logs    │ Push Spans
                                         │ (/metrics)   │              │
┌────────────────────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────┐
│ INFRASTRUCTURE & PODS                  │              │              │                                        │
│                                        │              │              │                                        │
│   ┌──────────────────────────┐         │              │              │                                        │
│   │ node-exporter            ├─────────┤              │            │                                        │
│   │ (Host CPU, Mem, Disk)    │         │              │              │                                        │
│   └──────────────────────────┘         │              │              │                                        │
│   ┌──────────────────────────┐         │              │              │                                        │
│   │ kms exporter             ├─────────┤              │              │                                        │
│   │ (Encryption / Key State) │         │              │              │                                        │
│   └──────────────────────────┘         │              │              │                                        │
│   ┌──────────────────────────┐         │              │              │                                        │
│   │ Loki Service             ├─────────┘              │              │                                        │
│   │ (/metrics Endpoint)      │                        │              │                                        │
│   └──────────────────────────┘                        │              │                                        │
│                                                       │              │                                        │
│   ┌───────────────────────────────────────────────────┴──────────────┼────────────────────────────────────┐   │
│   │ GRAFANA ALLOY (k8s-monitoring DaemonSet)                         │                                    │   │
│   │ Tails /var/log/pods (stdout/stderr) ─────────────────────────────┘                                    │   │
│   └───────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                 
```
#### Telemetry Responsibilities
 - Prometheus: Periodically scrapes /metrics endpoints from node-exporter, kms, cluster pods, and Loki itself to maintain historical metrics data.
 - Loki: Centralized log engine that indexes metadata labels and stores log streams in chunk storage.
 - Grafana Alloy (k8s-monitoring): DaemonSet agent that watches /var/log/pods, attaches Kubernetes metadata (namespace, pod, container), and pushes logs to Loki.

 - Grafana: Provides unified dashboards, ad-hoc exploration, cross-linking, and alerting.

---
### 2. Application Overview Dashboard (The "Golden Signals")
Purpose
High-level operational view for developers and on-call SREs to evaluate microservice health, request volumes, error spikes, and hardware pressure.
  ##### Dashboard Settings
   - Primary Data Source: Prometheus
   - Data Source Linking: Metric panels linked directly to Loki pre-filtered for {service="<service_name>"} at the exact target timestamp.

  | Panel Name        | Metric / Goal                                | PromQL Query                                                                                          |
|-------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Request Rate (RPS)| Total throughput across services              | sum(rate(http_requests_total[5m])) by (service)                                                       |
| Error Rate (%)    | Percentage of failing HTTP 5xx responses      | sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100          |
| p95 Latency       | 95th percentile request duration              | histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))        |
| Pod Restarts      | Unstable containers / CrashLoopBackOffs       | sum(changes(kube_pod_container_status_restarts_total[30m])) by (pod)                                  |
| Memory Saturation | Container memory usage vs. configured limit   | sum(container_memory_working_set_bytes) by (pod) / sum(kube_pod_container_resource_limits{resource="memory"}) by (pod) * 100 |



##### 3. Node Exporter & Infrastructure Dashboard
Purpose
Monitors underlying Linux node resource saturation and hardware health.

**Dashboard Settings**
 - Primary Data Source: Prometheus (scraping node-exporter)
 - Recommended Grafana *Dashboard ID: 1860 (Node Exporter Full)*

 | Panel Name         | Metric / Goal                           | PromQL Query                                                                                          |
|--------------------|-----------------------------------------|-------------------------------------------------------------------------------------------------------|
| CPU Utilization    | Percentage of total node CPU in use     | 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)                       |
| Memory Available   | Remaining physical RAM                  | node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100                                     |
| Disk Space Usage   | Root filesystem disk consumption        | 100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"}) |
| Network Throughput | Inbound/outbound interface traffic      | sum(rate(node_network_receive_bytes_total[5m])) by (instance)                                         |

##### 4. KMS Exporter Dashboard
Purpose
 Monitors Key Management Service (KMS) operations, request latency, and crypto-operation failures.

Dashboard Settings
- Primary Data Source: Prometheus (scraping kms exporter)

| Panel Name        | Metric / Goal                                | PromQL Query                                                                                          |
|-------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------|
| KMS Request Rate  | Operations per second (encrypt/decrypt/sign) | sum(rate(kms_requests_total[5m])) by (operation)                                                      |
| KMS Error Rate    | Failed cryptographic operations              | sum(rate(kms_requests_failed_total[5m])) by (operation, reason)                                       |
| Key Latency (p99) | 99th percentile crypto operation duration     | histogram_quantile(0.99, sum(rate(kms_request_duration_seconds_bucket[5m])) by (le, operation))       |


##### 5. Loki Operational & System Dashboard
Purpose
Monitors the ingestion rate, storage engine, chunk flushes, and query execution health of Loki itself.
Dashboard Settings
 - Primary Data Source: Prometheus (scraping Loki's /metrics endpoint)
 - Recommended Grafana *Dashboard IDs: 13407 (Operational)*, *14058 (Writes)*, *14057 (Reads)*

| Panel Name          | Metric / Goal                                        | PromQL Query                                                                                          |
|---------------------|------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Ingestion Rate      | Bytes per second pushed to Loki                      | sum(rate(loki_distributor_bytes_received_total[5m]))                                                  |
| Discarded Logs      | Dropped logs due to formatting or rate limits        | sum(rate(loki_discarded_samples_total[5m])) by (reason)                                               |
| Flush Failures      | Connection issues writing chunks to object storage   | sum(rate(loki_ingester_flush_failed_sweeps_total[5m]))                                                |
| Query Latency (p99) | Execution time of LogQL queries                      | histogram_quantile(0.99, sum(rate(loki_request_duration_seconds_bucket{route=~".*query.*"}[5m])) by (le)) |



```YAML
groups:
  - name: loki_alerts
    rules:
      - alert: LokiFlushFailed
        expr: loki_ingester_flush_failed_sweeps_total > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Loki failing to flush chunks to object storage"

      - alert: LokiHighLogDropRate
        expr: rate(loki_discarded_samples_total[5m]) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Loki dropping log entries due to rate limits or invalid timestamps"
 
```
##### 6. Grafana Alloy (k8s-monitoring) Shipper Dashboard
Purpose
Ensures pod log collection on node filesystems isn't lagging, buffering, or dropping logs before reaching Loki.

Dashboard Settings
 - Primary Data Source: Prometheus (scraping Alloy internal metrics)
 - Recommended Grafana Community Dashboard: 15632 (or official Alloy pipeline dashboard)

| Panel Name        | Metric / Goal                           | PromQL Query                                                                 |
|-------------------|-----------------------------------------|------------------------------------------------------------------------------|
| Active Log Targets| Number of discovered pod log files      | alloy_logging_active_targets_total                                           |
| Log Tail Lag      | Delay between file writes and collector reads | promtail_file_bytes_total - promtail_read_bytes_total                    |
| Pipeline Drops    | Unparseable or dropped log entries      | sum(rate(promtail_dropped_entries_total[5m])) by (reason)                    |


##### 7. Contextual Navigation & Incident Workflow
When an operational incident occurs, engineers navigate across telemetry pillars using standardized metadata (service, timestamp, trace_id):
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DETECT ANOMALY (PROMETHEUS)                                                  │
│                                                                                      │
│   Alert or Grafana Golden Signals panel indicates HTTP 5xx spike on service="backend"  │
│   [ Panel Action: Click "Explore Logs" ]                                             │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ Context Passed:
                                           │ - service="backend"
                                           │ - timestamp=12:45:00
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: ISOLATE LOG ERROR (LOKI)                                                     │
│                                                                                      │
│   Log Line: "ERROR DB Connection Timeout trace_id=4bf92f3577b34da6a3ce929d0e0e4736"  │
│   [ Line Action: Click Derived Field "TraceID" ]                                     │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ Context Passed:
                                           │ - trace_id="4bf92f3577b3..."
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ROOT CAUSE ANALYSIS (TEMPO / TRACING)                                        │
│                                                                                      │
│   Trace Gantt Chart displays execution flow:                                         │
│   ├── GET /todos (HTTP 200) ................................ [15ms]                  │
│   └── postgres.query "SELECT * FROM todos" ................. [5000ms - TIMEOUT]      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Tracing : Tempo
```
   +--------+
   | Alloy  |
   +--------+
       |
       v
   +--------+
   | Tempo  |
   +--------+
       |
       v
   +---------+
   | Grafana |
   +---------+
```
##### Tempo / Distributed Tracing Dashboard
Purpose
Ensures distributed trace spans emitted by application microservices are received, batched, and persisted properly.

Configuration
- Primary Data Source: Prometheus (scraping Tempo's /metrics endpoint)
- Recommended Grafana Community Dashboard: 14197 (Tempo Operational)

| Panel Name                   | Metric / Goal                                   | PromQL Query                                                                                          |
|-------------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Span Receive Rate             | Inbound spans per protocol (OTLP/Zipkin/Jaeger)| sum(rate(tempo_receiver_spans_received_total[5m])) by (protocol)                                      |
| Span Drop Rate                | Spans dropped due to queue congestion          | sum(rate(tempo_receiver_spans_dropped_total[5m]))                                                     |
| Compactor Outstanding Blocks  | Uncompacted block queue size                   | tempo_compactor_outstanding_blocks                                                                    |
#### Production Contextual Workflow & Data Linking
In a standard incident response workflow, engineers navigate seamlessly across telemetry pillars using standard identifiers (service_name, timestamp, and trace_id):
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DETECT ANOMALY (PROMETHEUS)                                                  │
│                                                                                      │
│   HTTP 5xx Error Spike Detected on service="backend" at 12:45:00                     │
│   [ Panel Action: Click "Explore Logs" Data Link ]                                   │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ Context Passed:
                                           │ - service="backend"
                                           │ - timestamp=12:45:00
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: ISOLATE LOG ERROR (LOKI)                                                     │
│                                                                                      │
│   Log Line: "ERROR DB Connection Timeout trace_id=4bf92f3577b34da6a3ce929d0e0e4736"  │
│   [ Line Action: Click Derived Field "TraceID" ]                                     │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ Context Passed:
                                           │ - trace_id="4bf92f3577b3..."
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ROOT CAUSE ANALYSIS (TEMPO)                                                  │
│                                                                                      │
│   Trace Gantt Chart displays execution flow:                                         │
│   ├── GET /todos (HTTP 200) ................................ [15ms]                  │
│   └── postgres.query "SELECT * FROM todos" ................. [5000ms - TIMEOUT]      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```
