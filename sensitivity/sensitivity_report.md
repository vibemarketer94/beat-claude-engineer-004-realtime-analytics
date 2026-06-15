# Sensitivity Sweep Report

This synthetic sweep names the scale, data-quality, and cost cliffs that would make the proposed architecture unsafe to cut over.

| Scenario | Spike | Event KB | Tenant skew | Late events | Export amp | Stream MB/s | Freshness seconds | Monthly cost | Gate | Action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| brief_peak | [Assumed] 10x | [Assumed] 1.0 | [Assumed] 2% | [Assumed] 1% | [Assumed] 1x | [Estimated] 5.65 | [Estimated] 3.9 | [Estimated] $7040.0/month | pass | eligible for cohort cutover after parity hold |
| large_payload_10x | [Assumed] 10x | [Assumed] 8.0 | [Assumed] 2% | [Assumed] 1% | [Assumed] 1x | [Estimated] 45.21 | [Estimated] 8.6 | [Estimated] $7302.5/month | manual_review | keep dual-write and require human go/no-go |
| tenant_skew_35pct | [Assumed] 10x | [Assumed] 1.0 | [Assumed] 35% | [Assumed] 1% | [Assumed] 1x | [Estimated] 5.65 | [Estimated] 3.9 | [Estimated] $9845.0/month | manual_review | keep dual-write and require human go/no-go |
| late_events_15pct | [Assumed] 10x | [Assumed] 1.0 | [Assumed] 2% | [Assumed] 15% | [Assumed] 1x | [Estimated] 5.65 | [Estimated] 8.8 | [Estimated] $8720.0/month | manual_review | keep dual-write and require human go/no-go |
| export_write_amp_6x | [Assumed] 10x | [Assumed] 1.0 | [Assumed] 2% | [Assumed] 1% | [Assumed] 6x | [Estimated] 5.65 | [Estimated] 3.9 | [Estimated] $10290.0/month | manual_review | keep dual-write and require human go/no-go |
| cost_ceiling_pressure | [Assumed] 20x | [Assumed] 16.0 | [Assumed] 35% | [Assumed] 15% | [Assumed] 8x | [Estimated] 180.84 | [Estimated] 29.7 | [Estimated] $55312.5/month | fail | do not cut over; resize, reduce exports, or change architecture |

## Reviewer Takeaway

The base design is not presented as infinitely elastic. Tenant skew, large payloads, late-event correction, export amplification, and reserve requirements are the explicit cliffs that trigger manual review or a failed cutover gate.
