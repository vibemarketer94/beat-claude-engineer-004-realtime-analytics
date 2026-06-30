# Validation Plan

## Metrics

| Metric | Detection | Gate |
|---|---|---|
| Event loss | Old/new count parity by tenant, type, and time bucket | [Estimated] less than 0.1% unexplained delta |
| Duplicate rate | Unique dedupe keys vs accepted events | [Estimated] less than 0.5% duplicate accepted rate |
| Freshness | Event received time to dashboard availability | [Observed target] less than 5 seconds p95 |
| Export correctness | Exported row counts and checksums by partition | [Estimated] less than 0.5% unexplained delta |
| Deletion completeness | Tombstone audit against hot, lake, export, and cache stores | [Estimated] 100% required surfaces acknowledged |
| Deletion immediacy | Live personalization/behavior state checked for tombstoned users | [Estimated] deleted users excluded from decisions within seconds, not on cache expiry |
| Intake authentication | Requests whose write key does not match the claimed tenant | [Estimated] auth-failure rate near 0%; all failures audited and DLQ-routed before any cohort cutover |

## Synthetic Harness Coverage

The local harness demonstrates the validation style with synthetic data:

- Normal case: clean events pass.
- Messy case: duplicate and out-of-order events are detected but the batch can pass after dedupe.
- Failure case: missing sequence windows or parity mismatch fails the accuracy gate and requires human review.

`modeling/migration_simulation.py` extends this with scaled synthetic dual-write scenarios. It generates `modeling/migration_simulation_report.md` and `modeling/migration_simulation_results.csv` for baseline, spike, and regression cases.

## Production Validation Queries

Production validation should compare:

- Intake accepted count vs stream accepted count.
- Stream accepted count vs Flink processed count.
- Flink processed count vs hot aggregate count.
- Raw S3 count vs warehouse export count.
- Deletion tombstones vs acknowledgements per storage surface.

## Response Playbook

- Loss detected: pause cohort rollout, replay from stream/S3, compare old/new parity, and keep old path serving.
- Duplicate spike: verify idempotency key generation, inspect retry path, and block affected tenant aggregates if needed.
- Freshness breach: degrade dashboard with freshness banner, shed non-critical exports, and scale processing.
- Deletion breach: stop related exports, quarantine affected partitions, and escalate to compliance owner.
