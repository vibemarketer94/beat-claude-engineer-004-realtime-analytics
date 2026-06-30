# Migration Runbook

## Delivery Timeline (2 senior engineers)

The brief gives [Observed] 2 senior engineers full-time, an MVP in [Observed] 3 months, and the full system in [Observed] 6 months. The phases below map onto that capacity. Managed services (Kinesis, Flink, DynamoDB) are the enabling choice: they remove cluster operations so two people can ship this.

| Window | Phase(s) | Outcome |
|---|---|---|
| Months 1-2 [Observed] | Phase 0-1 | SDK-compatible intake, Kinesis durable stream, S3 raw lake + replay, old-path instrumentation. No accepted event is unrecoverable. |
| Month 3 [Observed] | Phase 2-3 | Flink dedupe/aggregates, DynamoDB hot store, under-5-second [Observed] dashboards, dual-write, parity/freshness gates. MVP: real-time dashboards live for an internal + design-partner cohort with tenant rollback. |
| Months 4-5 [Observed] | Phase 3-4 | Personalization (Redis + decision API), behavioral segmentation, warehouse exports with checksums, GDPR/CCPA deletion workflow with per-surface acknowledgements and audit ledger. |
| Month 6 [Observed] | Phase 4-5 | Remaining tenant cohorts cut over, old reads retired after a full dual-write business cycle, replay/chaos drills and freshness SLO dashboards added. |

## Phase 0: Instrument Current Path

- Add request IDs, tenant IDs, received counts, accepted counts, and drop reasons to the current path.
- Establish baseline loss, duplicate, freshness, and export correctness metrics.
- Freeze public SDK contract and document server-side adapters for legacy payloads.

## Phase 1: Dual-Write

- Write every accepted event to the existing pipeline and the new durable stream.
- Keep the old pipeline as customer-serving source of truth.
- Compare per-tenant counts by event type and time bucket.

## Phase 2: Shadow Validation

- Run new dashboard aggregates in shadow for selected tenants.
- Gate expansion on freshness, loss, duplicate rate, export parity, and deletion propagation.
- Investigate mismatches before adding more tenants.

## Phase 3: Cohort Rollout

- Start with internal tenant and low-volume design partners.
- Move cohorts by traffic shape, not customer logo value.
- Keep rollback to old serving path for each tenant until cutover gates hold for [Assumed] 7 consecutive days.

## Phase 4: Cutover

- Switch dashboard reads to new hot store by tenant cohort.
- Keep dual-write active through one full business cycle.
- Publish customer-facing freshness degradation behavior before peak events.

## Phase 5: Post-Cutover

- Retire old serving reads after export, deletion, and dashboard parity remain stable.
- Keep raw event replay path and deletion audit path permanent.

## Rollback Criteria

Rollback a tenant cohort if any of these fire:

- [Estimated] Loss rate exceeds 0.1% for 15 minutes.
- [Estimated] Duplicate rate exceeds 0.5% for 15 minutes.
- [Observed target] Dashboard freshness exceeds 5 seconds for 30 minutes without graceful degradation.
- Export parity differs from old pipeline by more than [Estimated] 0.5%.
- Deletion workflow cannot prove propagation to hot, cold, and export surfaces.

## What Stays Human

- Migration go/no-go.
- Compliance deletion policy and exception handling.
- Customer-impacting rollback.
- Cost-versus-latency tradeoffs.
- Approval to relax accuracy gates during peak periods.

