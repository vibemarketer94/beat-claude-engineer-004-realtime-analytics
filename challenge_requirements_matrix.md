# Challenge Requirements Matrix

This matrix maps the public Engineer 004 prompt to the packet artifacts. It is not a substitute for the answer; it is a reviewer navigation aid.

| Prompt Requirement | Covered By | Notes |
|---|---|---|
| High-level system diagram with data flow from SDK to dashboard | `architecture.mmd`, `submission.md` | Diagram includes SDK, intake, stream, processor, hot store, dashboard, export, personalization, deletion, and observability. |
| Technology/services for each component and why over alternatives | `submission.md`, `cost_model.md` | Main answer explains Kinesis over MSK, Flink over Lambda consumers, DynamoDB hot aggregates, S3 lake. |
| Event data structure and identity/stitching | `event_contract.md`, `submission.md` | Includes `tenant_id:event_id`, anonymous-to-known identity events, schema versioning, and legacy SDK adapters. |
| Handle 50M+ events/day and 10x spikes | `cost_model.md`, `modeling/capacity_cost_report.md`, `sensitivity/sensitivity_report.md`, `submission.md`, `validation_plan.md` | Throughput math uses [Observed] 50M/day and [Observed] 10x spike with labeled assumptions, scenario output, and cliff-edge sensitivity. |
| Zero data loss / reliability | `submission.md`, `migration_runbook.md`, `validation_plan.md`, `validation_harness/` | Durable intake, at-least-once processing, idempotency, DLQ, replay, parity gates. |
| Move from current system without breaking things | `migration_runbook.md`, `submission.md` | Instrument, dual-write, shadow validation, cohort rollout, tenant rollback. |
| Rollback plan | `migration_runbook.md`, `submission.md` | Tenant-scoped rollback criteria and human approvals. |
| Validate data accuracy | `validation_plan.md`, `validation_harness/`, `modeling/migration_simulation_report.md`, `curveballs/curveball_report.md`, `evidence_log.md` | Count parity, duplicate rate, freshness, export checksums, deletion acknowledgements, synthetic dual-write gates, and failure-mode responses. |
| Trade-offs and risks | `submission.md`, `reviewer_scorecard.md`, `sensitivity/sensitivity_report.md` | Names optimizations, sacrifices, risks, more-time/more-budget choices, and scale/cost cliffs. |
| AWS constraint | `architecture.mmd`, `submission.md`, `cost_model.md` | All proposed services are AWS-native or fit AWS-hosted stack. |
| No SDK breaking change | `event_contract.md`, `migration_runbook.md`, `submission.md` | Intake adapters preserve existing SDK contract. |
| Multi-tenant 500+ customers | `architecture.mmd`, `event_contract.md`, `cost_model.md`, `submission.md` | Tenant ID is mandatory and included in partitions/keys/gates. |
| SOC 2, GDPR, CCPA | `submission.md`, `architecture.mmd`, `validation_plan.md` | Audit logs, rollout gates, deletion tombstones, deletion acknowledgements. |
| Written answer | `submission.md` | Main Markdown response. |
| Operating artifact | `operating_artifact.md`, `validation_harness/`, `benchmarks/`, `modeling/`, `curveballs/`, `sensitivity/`, `architecture.mmd`, `cost_model.md`, `validation_plan.md`, `run_reviewer_packet.sh` | Runnable scripts plus model/diagram/test plan, benchmark reports, before/after data, curveballs, sensitivity sweep, and generated traces. |
| Evidence log | `evidence_log.md` | Major claims mapped to labels and proof tiers. |
| Number source labels | `submission.md`, `cost_model.md`, `evidence_log.md` | Checked by `verify_packet.py`. |
| AI usage disclosure | `ai_usage.md` | Tools used, AI help, human decisions, checks, weak spots. |
| What breaks it | `submission.md`, `migration_runbook.md`, `validation_plan.md` | Failure modes, detection, response. |
| What stays human | `submission.md`, `migration_runbook.md`, `ai_usage.md` | Migration go/no-go, compliance, rollback, cost/latency approvals. |
