# Reviewer Walkthrough

Use this when a reviewer asks for a live explanation or private curveball follow-up.

## Five Minute Path

1. Start with `submission.md`: the thesis is migration safety and measurable correctness, not tool-name listing.
2. Open `architecture.mmd`: show SDK compatibility, durable intake, stream processing, hot aggregates, S3 replay/audit, warehouse export, personalization, deletion, and observability.
3. Run `./run_reviewer_packet.sh`: this creates `reviewer_run.log` and reruns tests, models, traces, the expected failing validation case, and packet verification.
4. Open `benchmarks/before_after_report.md`: show synthetic before/after loss and freshness improvement with a declared baseline and method.
5. Open `curveballs/curveball_report.md`: show how the design responds to tenant hotspots, missing event IDs, deletion during replay, export failure, backpressure, and clock skew.
6. Open `sensitivity/sensitivity_report.md`: show where the design stops being safe and requires manual review or a failed cutover gate.
7. Open `evidence_log.md`: show proof tiers, number labels, synthetic Tier 4 limits, and no Tier 5 overclaim.

## Curveball Responses

| Reviewer asks | Point to | Short answer |
|---|---|---|
| What if one tenant creates a hotspot? | `curveballs/curveball_report.md`, `sensitivity/sensitivity_report.md` | Keep dual-write, isolate tenant, and do not cut over shared reads until partition and hot-store pressure are safe. |
| What if legacy SDKs omit IDs? | `event_contract.md`, `curveballs/curveball_report.md` | Intake preserves SDK compatibility by assigning server IDs and warning metrics instead of rejecting all legacy traffic. |
| What if GDPR deletion lands during replay? | `validation_plan.md`, `curveballs/curveball_report.md` | Compliance tombstone reconciliation blocks cutover. Freshness loses to deletion correctness. |
| What if the new path looks cheaper only under friendly assumptions? | `sensitivity/sensitivity_report.md`, `cost_model.md` | The sensitivity sweep names payload, skew, late-event, export-amplification, and reserve cliffs. |
| What proves this packet is runnable? | `run_reviewer_packet.sh`, `reviewer_run.log`, `verification_report.md` | One command reruns the artifacts and records fresh logs. |

## What Not To Overclaim

- This is not production Tier 4 data.
- This is not Tier 5 independent verification unless CI or an external reviewer runs the replay.
- The synthetic benchmark proves operating reasoning and gates, not exact AWS production performance.
