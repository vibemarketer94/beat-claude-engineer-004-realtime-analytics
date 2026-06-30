# Event Contract

## Required Fields

| Field | Purpose | Rule |
|---|---|---|
| `tenant_id` | Multi-tenant isolation | Required; partition key prefix for all stores. |
| `event_id` | Idempotency | Required; unique within tenant. |
| `anonymous_id` | Pre-login behavior stitching | Required unless `user_id` exists. |
| `user_id` | Known user stitching | Optional; linked to prior anonymous IDs by identity event. |
| `event_type` | Routing and analytics | Required; controlled vocabulary with custom-event namespace. |
| `occurred_at` | Event time | Required; ISO timestamp from SDK. |
| `received_at` | Server time | Added at intake. |
| `sequence` | Loss and ordering checks | Monotonic per SDK session when available. |
| `properties` | Event payload | JSON object; schema-limited and size-limited. |
| `schema_version` | Evolution | Required; defaults from intake adapter for older SDKs. |

## Intake Authentication and Transport

The browser SDK is public, so a client-supplied `tenant_id` cannot be trusted on its own. The trust boundary is intake:

- Each tenant has a server-side write key (provisioned in the PostgreSQL control plane). Intake resolves the key to a tenant and rejects any request whose claimed `tenant_id` does not match the key's tenant.
- Rejected/auth-failed requests go to the DLQ with an audit entry; they are never written to a tenant's stream. Auth-failure rate is a monitored rollout gate.
- All traffic is encrypted in transit (TLS) as well as at rest (KMS). Exports to customer warehouses use short-lived signed credentials, not stored secrets.
- Downstream isolation is enforced with per-tenant IAM scoping: a worker or export job can read only its own tenant's S3 partitions, and dashboard queries are tenant-scoped (no cross-tenant scans).

## Identity and Dedupe Rules

- Dedupe key: `tenant_id:event_id`.
- Tenant isolation is mandatory before any aggregate write.
- Identity stitching is append-only: anonymous IDs can link to a known user, but old raw events are not rewritten during hot-path processing.
- On a GDPR/CCPA delete, the anonymous-to-known identity link is cleared (or irreversibly hashed) so the person cannot be re-identified if an old anonymous ID is later reused.
- Deletion takes effect immediately for live personalization (behavior state is tombstoned synchronously), not on natural cache expiry.
- Late events update event-time windows when within retention; beyond retention they enter audit/replay flow.
- Bad schema events go to DLQ with tenant, reason, and raw payload reference.

## Compatibility

The SDK contract cannot break. Intake adapters should fill missing server-side fields, map legacy event names, and emit schema warnings before rejecting traffic.

