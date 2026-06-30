# Engineer 004: Real-Time Analytics Pipeline

## Thesis

The rebuild should optimize for migration safety and measurable correctness before service-name novelty. The hard part is not naming Kinesis, Kafka, Flink, and S3; it is proving the new path can run beside the old one, stay under the $50K/month ceiling [Observed], handle 50M events/day [Observed] with 10x spikes [Observed], preserve existing SDK integrations, support 500+ tenants [Observed], and detect data loss before customers do.

## Operating Artifact

This submission includes a repo-style operating artifact, described in `operating_artifact.md`. It includes an architecture diagram, test plan, benchmark model, migration simulation, generated traces, and runnable scripts. From `engineer-004-packet/`, run:

```bash
./run_reviewer_packet.sh
python3 validation_harness/run_validation.py validation_harness/sample_events.jsonl
python3 -m unittest benchmarks/test_old_vs_new_benchmark.py
python3 -m unittest curveballs/test_curveball_scenarios.py
python3 -m unittest sensitivity/test_sensitivity_model.py
python3 benchmarks/old_vs_new_benchmark.py
python3 modeling/capacity_cost_model.py
python3 modeling/migration_simulation.py
python3 curveballs/curveball_scenarios.py
python3 sensitivity/sensitivity_model.py
python3 verify_packet.py
```

The validation harness intentionally exits with code 1 [Observed] because the sample includes a bad migration case; the point is to prove the gate fails and routes to human review. The before/after benchmark measures synthetic improvement from the broken current pipeline to the proposed design: peak expected event loss improves from 3.032% to 0.088% [Observed synthetic], and p95 freshness improves from 1,320 seconds to 4.2 seconds [Observed synthetic]. The capacity model generates MVP, full, large-payload, and 2x-growth scenarios [Estimated]. The migration simulation generates baseline, spike, and regression dual-write scenarios. The curveball and sensitivity artifacts add 6 reviewer-follow-up failure modes [Observed synthetic] and 6 scale/cost cliff scenarios [Observed synthetic].

## 1. Architecture and Technology Choices

Existing browser SDK events continue to hit a compatibility-preserving AWS intake layer; customers should not update SDKs. CloudFront and regional API intake workers add server-side fields, validate tenant/schema/idempotency, write accepted events to Kinesis Data Streams, and route rejected payloads to SQS DLQ. Managed Apache Flink reads Kinesis for dedupe, sessionization, behavioral segmentation, recent-behavior triggers, and dashboard aggregates. DynamoDB stores hot tenant/time-bucket aggregates for dashboards; Redis stores short-lived behavior state for personalization. S3 stores raw and normalized events partitioned by tenant/date for replay, audit, validation, and export. Glue/Athena and export jobs feed Snowflake or BigQuery. PostgreSQL remains the control plane for tenants, schemas, export configuration, and deletion workflows.

See `architecture.mmd` for the data flow from SDK to dashboard, personalization, export, and deletion paths.

I would choose Kinesis over MSK for the MVP because the team has 12 engineers [Observed] and only 2 seniors [Observed] dedicated full-time; managed shard/on-demand operations are a better fit than Kafka cluster operations. I would choose Flink over ad hoc Lambda consumers because event-time windows, late events, dedupe, and behavior patterns are core requirements. I would choose DynamoDB hot aggregates over querying the lake because dashboards need less than 5 second freshness [Observed]. I would keep S3 as the replay/audit source because hot stores are derived and disposable.

Event identity is `tenant_id:event_id`; all aggregate keys include tenant. User identity stitching links anonymous IDs to known users through append-only identity events rather than rewriting raw history. Legacy SDK payloads are adapted at intake with `schema_version`, `received_at`, and validation warnings so the public SDK contract does not break. See `event_contract.md`.

SOC 2 support comes from audit logs, change-controlled rollout gates, access-controlled tenant configuration, and deletion evidence. GDPR/CCPA support uses deletion tombstones propagated to Redis, DynamoDB, S3/delete manifests, export jobs, and audit logs. The "2" in SOC 2 is a framework name, not a quantitative claim.

## 2. Scale, Reliability, and Migration

The brief gives 50M events/day [Observed]. That is 579 events/sec [Estimated] on average and 5,790 events/sec [Estimated] at a 10x peak [Observed]. With a 1 KB event envelope [Assumed], peak ingest is 5.79 MB/sec [Estimated] and monthly raw ingest is about 1.5 TB [Estimated]. The generated scenario model estimates $4.3K-$8.8K/month [Estimated] for the modeled core paths; with conservative production reserves for HA, support overhead, higher write amplification, and customer-specific exports, plan for about $15K-$35K/month [Estimated]. Both bands stay below the $50K/month ceiling [Observed] while showing which assumptions must be measured. See `modeling/capacity_cost_report.md`, `modeling/capacity_cost_results.csv`, and `modeling/capacity_cost_trace.log`. For Tier 4-style synthetic before/after data, see `benchmarks/before_after_report.md`.

Zero data loss is an operating target, not a magic guarantee. The design uses durable intake, at-least-once processing, idempotent writes, DLQs, replay from Kinesis/S3, and parity checks. Backpressure should degrade customer-visible freshness before dropping accepted events. Noisy tenants get quotas and isolated partitions; high-volume tenants can be moved to dedicated streams or tables if needed.

Migration is tenant-cohort based:

1. Instrument current intake and establish old-path baselines.
2. Dual-write accepted events to old and new paths.
3. Run shadow dashboards from the new path while old path remains source of truth.
4. Gate rollout on loss, duplicate rate, freshness, export parity, and deletion propagation.
5. Cut over dashboard reads by cohort after gates hold for 7 consecutive days [Assumed].
6. Keep dual-write through one full business cycle before retiring old reads.

Rollback remains tenant-scoped. If loss, duplicate rate, freshness, export parity, or deletion checks fail, the tenant stays or returns to the old serving path while the new path replays and reconciles. See `migration_runbook.md`.

Validation must be continuous: old/new count parity by tenant/type/time bucket, dedupe key uniqueness, freshness from receive time to visible aggregate, export row counts and checksums, and deletion tombstone acknowledgements across all storage surfaces. The included `validation_harness/` demonstrates this approach on synthetic events. It passes clean and messy duplicate/out-of-order cases, and fails a missing-sequence/parity-mismatch case with a human-review recommendation. `modeling/migration_simulation_report.md` adds scaled synthetic dual-write scenarios for baseline, spike, and regression conditions; `modeling/migration_simulation_trace.log` records the latest local run.

## 3. Trade-offs and Risks

This design optimizes for correctness, migration safety, operational simplicity, and customer-visible freshness. It sacrifices some Kafka portability, some ad hoc dashboard flexibility, and some real-time exactness for late events. The trade is intentional: a 3% peak event-loss problem [Observed] is more damaging than a slightly less flexible streaming substrate.

Main risks:

- Schema drift: mitigated with versioned contracts, adapters, DLQ, and warning metrics.
- Retry duplicates: mitigated with `tenant_id:event_id` idempotency and harness-tested duplicate detection.
- Late or out-of-order events: handled with event-time windows, allowed lateness, and audit/replay flow.
- Tenant hot spots: controlled by quotas, partitioning, and per-tenant rollout gates.
- Export cost or incorrectness: controlled by S3 partitioning, checksums, and scheduled per-tenant exports.
- Deletion incompleteness: controlled by tombstones, per-surface acknowledgements, and compliance escalation.
- False migration confidence: controlled by dual-write, shadow validation, and rollback criteria.

With more time or budget, I would add a production-scale replay drill, tenant-level chaos tests, customer-visible freshness SLO dashboards, CI-backed replay of this packet, and independent verification from a real partner tenant. I would not automate migration go/no-go, compliance deletion exceptions, customer-impacting rollback, or cost-versus-latency approvals. AI can draft runbooks and summarize anomalies, but those decisions stay human.

## Submission Packet

- `architecture.mmd`: system diagram
- `operating_artifact.md`: artifact index and run commands
- `benchmarks/`: synthetic before/after benchmark, unit tests, CSV, and trace
- `curveballs/`: reviewer-follow-up failure scenarios, tests, CSV, and trace
- `sensitivity/`: scale, skew, payload, export, and budget-cliff sweep
- `challenge_requirements_matrix.md`: prompt coverage matrix
- `cost_model.md`: source-labeled cost and throughput model
- `modeling/`: runnable scenario cost model and migration simulation
- `event_contract.md`: event identity, schema, dedupe, and tenant rules
- `migration_runbook.md`: dual-write, rollout, rollback, and human approvals
- `validation_plan.md`: metrics, gates, and response playbook
- `validation_harness/`: runnable synthetic proof for dedupe, sequence, and parity checks
- `evidence_log.md`: claims mapped to source labels and proof tiers
- `ai_usage.md`: AI disclosure
- `run_reviewer_packet.sh`: one-command reviewer replay
- `walkthrough.md`: live-review guide
