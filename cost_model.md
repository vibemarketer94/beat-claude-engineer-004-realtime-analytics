# Cost and Throughput Model

This is a sizing artifact, not a quote. Prices and quotas should be rechecked before submission.

For scenario output generated from the model, see `modeling/capacity_cost_report.md` and `modeling/capacity_cost_results.csv`.

## Inputs

| Item | Value | Label | Source |
|---|---:|---|---|
| Daily event volume | 50,000,000 events/day | [Observed] | Engineer 004 brief |
| Peak multiplier | 10x | [Observed] | Engineer 004 brief |
| Tenant count | 500+ tenants | [Observed] | Engineer 004 brief |
| Freshness target | less than 5 seconds | [Observed] | Engineer 004 brief |
| Average event envelope | 1 KB/event | [Assumed] | Conservative planning placeholder; replace with measured p50/p95 event size in production |
| Month length | 30 days | [Assumed] | Planning simplification |
| Stream read fanout | 2 consumers | [Assumed] | Flink processor plus archival/export path |

## Throughput

| Metric | Formula | Result | Label |
|---|---|---:|---|
| Average events/sec | 50,000,000 / 86,400 | 579 events/sec | [Estimated] |
| Peak events/sec | 579 * 10 | 5,790 events/sec | [Estimated] |
| Average ingest | 579 * 1 KB | 0.58 MB/sec | [Estimated] |
| Peak ingest | 5,790 * 1 KB | 5.79 MB/sec | [Estimated] |
| Monthly raw ingest | 50,000,000 * 1 KB * 30 | about 1.5 TB/month | [Estimated] |

Interpretation: the traffic is not extreme by streaming standards, but the system still needs durable intake, replay, tenant isolation, and parity checks because the current issue is [Observed] 3% event loss during peak periods.

## Service Cost Posture

| Component | Planning Basis | Monthly Band | Label | Source |
|---|---|---:|---|---|
| Kinesis Data Streams intake | about 1.5 TB ingest/month plus 2 read consumers | $100-$500 | [Estimated] | AWS Kinesis pricing and quotas |
| Managed Apache Flink | 8-24 KPUs continuous, adjusted after load test | $700-$2,200 | [Estimated] | AWS Managed Service for Apache Flink pricing |
| S3 raw + normalized lake | 3 TB active standard storage before lifecycle | $70-$150 | [Estimated] | AWS S3 pricing |
| DynamoDB hot aggregates | tenant/time bucket counters, on-demand or provisioned after benchmark | $1,000-$6,000 | [Estimated] | Requires production read/write shape |
| Redis behavior state | clustered ElastiCache/Redis for recent behavior and trigger state | $1,000-$4,000 | [Estimated] | Requires memory and HA sizing |
| Ingestion workers | autoscaled ECS/Fargate or EC2 service behind load balancer | $1,000-$5,000 | [Estimated] | Requires CPU per event benchmark |
| Observability and DLQ retention | CloudWatch metrics/logs, SQS DLQ, alarms | $500-$3,000 | [Estimated] | Depends on log sampling and retention |
| Warehouse/export support | Athena/Glue plus customer export jobs | $500-$5,000 | [Estimated] | Depends on scan volume and export cadence |

Generated model posture: [Estimated] $4,300-$8,800/month for modeled core scenarios. Production planning posture: [Estimated] reserve up to $15,000-$35,000/month after HA, higher write amplification, support overhead, and customer-specific exports. Both stay below the [Observed] $50,000/month ceiling if log volume, hot-store retention, and warehouse scans are controlled.

## Cost Controls

- Keep raw events in S3 with lifecycle rules; do not serve dashboards from the data lake.
- Store hot aggregates by tenant/time bucket with short retention.
- Sample verbose logs and emit metrics for all events.
- Use tenant-level quotas and backpressure before noisy tenants starve shared processors.
- Cap warehouse export scan volume with partition pruning and per-tenant export schedules.

## Sources

- AWS Kinesis Data Streams pricing: https://aws.amazon.com/kinesis/data-streams/pricing/
- AWS Kinesis Data Streams quotas: https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html
- AWS Managed Service for Apache Flink pricing: https://aws.amazon.com/managed-service-apache-flink/pricing/
- AWS S3 pricing: https://aws.amazon.com/s3/pricing/
- AWS MSK pricing alternative: https://aws.amazon.com/msk/pricing/
- AWS Redshift pricing alternative: https://aws.amazon.com/redshift/pricing/
- AWS OpenSearch Service pricing alternative: https://aws.amazon.com/opensearch-service/pricing/
