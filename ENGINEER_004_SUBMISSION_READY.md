# Engineer 004: Real-Time Analytics Pipeline

**Runnable artifact repo:** https://github.com/vibemarketer94/beat-claude-engineer-004-realtime-analytics
**One-command reviewer replay:** `./run_reviewer_packet.sh`
**Independently reproduced:** GitHub Actions re-runs the full replay on every push.
[![Reviewer Replay](https://github.com/vibemarketer94/beat-claude-engineer-004-realtime-analytics/actions/workflows/reviewer-replay.yml/badge.svg)](https://github.com/vibemarketer94/beat-claude-engineer-004-realtime-analytics/actions/workflows/reviewer-replay.yml)

---

## Thesis

Rebuild for migration safety and measurable correctness, not service-name novelty. Naming Kinesis, Flink, and S3 is the easy part. The hard part is proving the new path can run beside the old one, stay under the $50K/month ceiling [Observed], handle 50M events/day [Observed] with 10x spikes [Observed], preserve existing SDKs, support 500+ tenants [Observed], and detect data loss before customers do. So the design is judged here on dual-write, parity gates, tenant isolation, compliance, and rollback — the things a generic architecture answer skips.

---

## 1. Architecture and Technology Choices

Existing browser SDK traffic keeps its public contract. CloudFront and regional intake workers add server-side fields, validate tenant/schema/idempotency, write accepted events to Kinesis Data Streams, and route rejected payloads to an SQS dead-letter queue. Managed Apache Flink reads Kinesis for dedupe, sessionization, behavioral segmentation, recent-behavior triggers, and dashboard aggregates. DynamoDB stores hot tenant/time-bucket aggregates; Redis stores short-lived behavior state for personalization. S3 stores raw and normalized events by tenant/date for replay, audit, validation, and export. Glue/Athena and export jobs feed Snowflake or BigQuery. PostgreSQL stays the control plane for tenants, schemas, export config, and deletion workflows.

![Architecture: data flow from SDK through intake, stream processing, hot serving, lake, exports, personalization, and deletion](architecture.png)

**Why these services over alternatives.** Kinesis over MSK for the MVP, because the team has 12 engineers [Observed] and only 2 dedicated seniors [Observed]; managed shard/on-demand operation beats owning a Kafka cluster. Flink over ad-hoc Lambda consumers, because event-time windows, late events, dedupe, and behavior patterns are core requirements, not extras. DynamoDB hot aggregates over querying the lake, because dashboards need under-5-second [Observed] freshness. S3 stays the replay/audit source of truth, because hot stores are derived and disposable.

**Event identity and stitching.** Event identity is `tenant_id:event_id`; every aggregate key includes the tenant. A legacy payload missing `event_id` gets a deterministic server id plus a schema warning, so the SDK contract never breaks. Identity stitching is append-only: anonymous-to-known events link identities for future aggregation without rewriting raw history; conflicts keep both ids, mark one canonical in the control plane, and are replay-corrected from S3.

**Behavioral segmentation and personalization.** Flink keeps per-tenant, per-user event-type counters in event-time windows, so a brief-style rule like "viewed pricing 3x [Observed] in a session" materializes a segment-membership flag into DynamoDB (and Redis for live triggers) that dashboards and the personalization API read directly — no rescan of the lake. The same counters feed the recent-behavior triggers, so segmentation and personalization share one stateful path rather than two.

**Trust boundary and tenant isolation.** The browser SDK is public, so intake can't trust a client-supplied `tenant_id`. Each tenant has a server-side write key; intake verifies the key resolves to the claimed tenant in the control plane and sends mismatches to the DLQ with an audit entry. From there `tenant_id` is mandatory on every partition, aggregate key, cache key, and export, and per-tenant access scoping keeps one tenant's data unreadable by another's jobs and queries.

**The judgment that protects the migration.** New-path gates compare against *accepted intake*, not against the broken old pipeline's counts. The current system loses about 3% at peak [Observed], so matching it would bless data loss. Gating against accepted intake is what lets "zero data loss" mean something measurable.

**Compliance.** SOC 2 comes from KMS-encrypted storage, encryption in transit (TLS), least-privilege IAM, audit logs, change-controlled rollout gates, and deletion evidence. GDPR/CCPA uses deletion tombstones propagated to Redis, DynamoDB, S3/delete manifests, exports, and an append-only audit ledger; a delete also clears the anonymous-to-known identity link (no re-identification) and takes effect immediately for live personalization, not on cache expiry. We erase every copy in our systems and drop the person from future exports; data already in a customer's own warehouse is theirs to remove, and we supply deletion proof.

---

## 2. Scale, Reliability, and Migration

**Throughput.** 50M events/day [Observed] is about 579 events/sec [Estimated] average and about 5,790 events/sec [Estimated] at a 10x peak [Observed]. At a 1 KB envelope [Assumed], peak ingest is about 5.79 MB/sec [Estimated] and raw ingest is about 1.5 TB/month [Estimated]. This is not extreme by streaming standards — which is exactly why the current 3% peak loss [Observed] is an architecture-and-operations problem, not a raw-volume one.

**Cost.** The runnable model puts the core paths at about $4.3K–$8.8K/month [Estimated]; with conservative production reserves for HA, write amplification, support, and customer exports, plan for about $15K–$35K/month [Estimated]. Both stay under the $50K/month ceiling [Observed], and the sensitivity sweep names exactly where that breaks.

**Zero-loss posture.** The 10x spike [Observed] is absorbed at the front door by Kinesis on-demand (or pre-provisioned shard headroom) and autoscaling intake workers, so the burst never reaches a fragile component unbuffered. Then: durable intake, at-least-once processing, idempotent writes, DLQs, Kinesis/S3 replay, and parity checks. Backpressure degrades customer-visible freshness *before* dropping accepted events. Noisy tenants get quotas and isolated partitions; high-volume tenants can move to dedicated streams or tables.

**Migration (tenant-cohort based).** Instrument the old path and baseline it; dual-write accepted events to old and new; run shadow dashboards from the new path while the old path stays source of truth; gate rollout on loss, duplicate rate, freshness, export parity, and deletion propagation; cut over reads by cohort only after gates hold for 7 consecutive days [Assumed]; keep dual-write through one full business cycle before retiring old reads. Rollback is tenant-scoped: if any gate fails, that tenant returns to the old serving path while the new path replays and reconciles.

**Delivery plan for the team in the brief.** Two senior engineers [Observed], MVP in 3 months [Observed], full system in 6 months [Observed]. Managed services are the enabling choice — they let two people ship this without standing up cluster operations.

- **Months 1–2 [Observed] — durable intake + safety net.** SDK-compatible intake layer (validation, idempotency, DLQ), Kinesis durable stream, S3 raw lake with replay, and instrumentation of the old path for baselines. Outcome: no accepted event is unrecoverable.
- **Month 3 [Observed] — MVP cutover for a cohort (the riskiest milestone).** Flink dedupe/sessionization, DynamoDB hot aggregates, under-5-second [Observed] dashboards, dual-write, and the parity/freshness gates. Most moving parts land here, so it carries the most schedule buffer and the first rollback drill. Outcome: real-time dashboards live for an internal + design-partner cohort on the new path, with tenant rollback.
- **Months 4–5 [Observed] — personalization, exports, compliance.** Redis behavior state and personalization API, behavioral segmentation, warehouse exports with checksums, and the GDPR/CCPA deletion workflow with per-surface acknowledgements and audit ledger.
- **Month 6 [Observed] — full rollout.** Move remaining tenant cohorts, retire old reads after a full dual-write business cycle, add replay/chaos drills and freshness SLO dashboards.

**Validation.** Continuous: old/new count parity by tenant/type/time bucket, dedupe-key uniqueness, receive-to-visible freshness, export row counts and checksums, and deletion-tombstone acknowledgements across every storage surface. The runnable harness demonstrates this on synthetic events: clean and messy duplicate/out-of-order cases pass; a missing-sequence/parity-mismatch case fails and routes to human review.

---

## 3. Trade-offs and Risks

This design optimizes for correctness, migration safety, operational simplicity, and customer-visible freshness. It sacrifices some Kafka portability, some ad-hoc dashboard flexibility, and some exact real-time correction for late events. That trade is intentional: a 3% peak event-loss problem [Observed] is worse than a less-portable streaming substrate.

Main risks and mitigations: schema drift (versioned contracts, adapters, DLQ, warning metrics); retry duplicates (`tenant_id:event_id` idempotency, harness-tested detection); late/out-of-order events (event-time windows, allowed lateness, audit/replay); tenant hot spots (quotas, partitioning, per-tenant gates); export cost/correctness (S3 partitioning, checksums, scheduled exports); deletion incompleteness (tombstones, per-surface acknowledgements, escalation); false migration confidence (dual-write, shadow validation, rollback criteria).

With more time or budget: a production-scale replay drill, tenant-level chaos tests, customer-visible freshness SLO dashboards, and independent verification from a real partner tenant.

---

*End of written answer. The items below are required packet components; per the brief, diagrams, links, and artifacts do not count toward the page limit.*

---

## What Breaks It

- Target AWS region/account quotas are lower than assumed → raise Kinesis/Flink capacity before cutover.
- Event envelopes are much larger than 1 KB [Assumed], or export write amplification is extreme → cost/freshness gates fail (the sensitivity sweep shows this).
- Legacy SDK payloads lack both stable client ids and stable payload fields → server-side idempotency weakens; those events take warning/review handling.
- Deletion tombstones do not reconcile across hot store, lake, cache, and exports → block tenant cutover.
- A single tenant dominates shared partitions → durable but not safe for read cutover without isolation.
- Private reviewer data differs materially from the public brief → rerun the model with those inputs.

## What Stays Human

Migration go/no-go, compliance deletion exceptions, customer-impacting rollback, tenant isolation for high-risk accounts, and cost-versus-latency approvals. The system can surface parity, freshness, duplicate, export, deletion, and cost evidence; accountability for business and compliance risk stays with people.

## Proof and Artifact Access

Everything below is inspectable in the repo with no credentials or private data. `./run_reviewer_packet.sh` reruns the tests, models, validation harness, and packet verifier and regenerates the logs — and GitHub Actions runs that same replay on every push (badge above), so the proof is reproducible off my machine.

| Claim | Source label | Proof tier | Where |
|---|---|---:|---|
| Brief constraints (50M/day, 10x, 500+ tenants, <5s, $50K, SOC2/GDPR/CCPA) | [Observed] | 3 | Public Engineer 004 brief |
| Average/peak ~579 / ~5,790 events/sec; core cost under ceiling | [Estimated] | 2 | `cost_model.md`, `modeling/` |
| Kinesis/Flink/S3 fit the workload in supported regions | [Benchmarked] | 3 | AWS pricing/quota links in `cost_model.md` |
| Synthetic peak loss 3.0%→0.1% and p95 freshness 22 min→4.2s | [Estimated] | 4 | `benchmarks/before_after_report.md` (synthetic before/after) |
| Replay is reproducible in a clean environment | [Observed] | 3 | Green GitHub Actions run; `reviewer_run.log` |

Full detail lives in the repo (these are links, not page-count): `evidence_log.md` (every claim, label, and tier), `operating_artifact.md` (artifact index), `ai_usage.md` (AI disclosure), `migration_runbook.md`, `validation_plan.md`, `curveballs/`, and `sensitivity/`.

## Number Source Labels

Every load-bearing number is labeled with one of the four public labels: [Observed] (measured from a real system or the brief), [Estimated] (own reasoning), [Benchmarked] (named external source), or [Assumed] (placeholder). Synthetic benchmark outputs are labeled [Estimated], because they come from a runnable model rather than production — the before/after benchmark still counts as Tier 4 evidence (measured change with a clear method), not as production data. Framework names like SOC 2 and section numbers are not quantitative claims.

## AI Usage Disclosure (summary; full version in `ai_usage.md`)

AI (ChatGPT/Codex) helped structure the packet around the public scoring guide, draft the architecture and artifacts, generate synthetic validation/benchmark/curveball/sensitivity cases under TDD, and build the one-command replay. Human decisions: centering migration/correctness/compliance, choosing a narrow honest harness over a fake production stack, keeping confidential data out, and checking brief/scoring coverage, AWS links, replay output, number labels, and evidence tiers. Known weak spots: the cost model is a planning model, not an AWS quote; the harness and sweeps are synthetic, not production load tests; CI reproduces the replay but no external human or customer has verified the result, so no independent human verification (the top proof tier) is claimed.
