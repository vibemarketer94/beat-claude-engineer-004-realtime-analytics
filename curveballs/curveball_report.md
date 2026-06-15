# Curveball Scenario Report

These scenarios are designed for private-review follow-ups: bad inputs, traffic cliffs, compliance conflicts, and partial cutovers.

| Scenario | Input | Gate | Loss budget OK | Operating action | Reason |
|---|---|---|---|---|---|
| tenant_hotspot | [Observed synthetic] one tenant produces 35% of peak events | manual_review | yes | isolate tenant and keep old read path | Shared stream stays durable, but tenant-specific hot partitions need isolation before read cutover. |
| missing_event_id | [Observed synthetic] legacy SDK payload omits event_id | pass_with_warning | yes | accept with server id and warning | No SDK breaking change: intake assigns deterministic server id and emits schema warning metric. |
| gdpr_delete_during_replay | [Observed synthetic] delete request arrives while replay rebuilds aggregates | fail | yes | block cutover until tombstones reconcile | Compliance deletion proof beats freshness; replay must apply tombstones before serving customer reads. |
| warehouse_export_failure | [Observed synthetic] BigQuery export checksum differs after retry | fail | yes | pause export cutover and regenerate from S3 partition | Dashboard path can pass while warehouse export stays old-path until row counts and checksum reconcile. |
| kinesis_backpressure | [Observed synthetic] Kinesis write throttles for 90 seconds during spike | manual_review | yes | shed freshness, buffer accepted events, and request shard/on-demand increase | Freshness can degrade, but accepted events must stay durable and replayable. |
| sdk_clock_skew | [Observed synthetic] client event_time is 48 hours behind received_at | pass_with_warning | yes | use received_at for freshness SLO and event_time for late-window analytics | Skew should not break ingest or dashboard freshness; late-event correction handles analytics. |

## Reviewer Takeaway

The architecture does not treat all failures as generic incidents. It keeps accepted events durable, blocks compliance-unsafe cutovers, and allows dashboard freshness to degrade before data loss.
