# Migration Runbook

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

