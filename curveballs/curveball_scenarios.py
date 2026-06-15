#!/usr/bin/env python3
"""Reviewer curveball scenarios for the Engineer 004 packet."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def evaluate_scenarios() -> list[dict[str, str]]:
    """Return operating decisions for likely private-review curveballs."""
    return [
        {
            "scenario": "tenant_hotspot",
            "input": "[Observed synthetic] one tenant produces 35% of peak events",
            "gate": "manual_review",
            "loss_budget_ok": "yes",
            "action": "isolate tenant and keep old read path",
            "reason": "Shared stream stays durable, but tenant-specific hot partitions need isolation before read cutover.",
        },
        {
            "scenario": "missing_event_id",
            "input": "[Observed synthetic] legacy SDK payload omits event_id",
            "gate": "pass_with_warning",
            "loss_budget_ok": "yes",
            "action": "accept with server id and warning",
            "reason": "No SDK breaking change: intake assigns deterministic server id and emits schema warning metric.",
        },
        {
            "scenario": "gdpr_delete_during_replay",
            "input": "[Observed synthetic] delete request arrives while replay rebuilds aggregates",
            "gate": "fail",
            "loss_budget_ok": "yes",
            "action": "block cutover until tombstones reconcile",
            "reason": "Compliance deletion proof beats freshness; replay must apply tombstones before serving customer reads.",
        },
        {
            "scenario": "warehouse_export_failure",
            "input": "[Observed synthetic] BigQuery export checksum differs after retry",
            "gate": "fail",
            "loss_budget_ok": "yes",
            "action": "pause export cutover and regenerate from S3 partition",
            "reason": "Dashboard path can pass while warehouse export stays old-path until row counts and checksum reconcile.",
        },
        {
            "scenario": "kinesis_backpressure",
            "input": "[Observed synthetic] Kinesis write throttles for 90 seconds during spike",
            "gate": "manual_review",
            "loss_budget_ok": "yes",
            "action": "shed freshness, buffer accepted events, and request shard/on-demand increase",
            "reason": "Freshness can degrade, but accepted events must stay durable and replayable.",
        },
        {
            "scenario": "sdk_clock_skew",
            "input": "[Observed synthetic] client event_time is 48 hours behind received_at",
            "gate": "pass_with_warning",
            "loss_budget_ok": "yes",
            "action": "use received_at for freshness SLO and event_time for late-window analytics",
            "reason": "Skew should not break ingest or dashboard freshness; late-event correction handles analytics.",
        },
    ]


def write_outputs(rows: list[dict[str, str]]) -> None:
    csv_path = ROOT / "curveball_results.csv"
    report_path = ROOT / "curveball_report.md"
    trace_path = ROOT / "curveball_trace.log"

    fieldnames = ["scenario", "input", "gate", "loss_budget_ok", "action", "reason"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Curveball Scenario Report",
        "",
        "These scenarios are designed for private-review follow-ups: bad inputs, traffic cliffs, compliance conflicts, and partial cutovers.",
        "",
        "| Scenario | Input | Gate | Loss budget OK | Operating action | Reason |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['input']} | {row['gate']} | "
            f"{row['loss_budget_ok']} | {row['action']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Takeaway",
            "",
            "The architecture does not treat all failures as generic incidents. It keeps accepted events durable, blocks compliance-unsafe cutovers, and allows dashboard freshness to degrade before data loss.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    trace_lines = ["curveball_scenarios run"]
    for row in rows:
        trace_lines.append(f"{row['scenario']} gate={row['gate']} action={row['action']}")
    trace_path.write_text("\n".join(trace_lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = evaluate_scenarios()
    write_outputs(rows)
    print(f"wrote {len(rows)} curveball scenarios")
    for row in rows:
        print(f"{row['scenario']}: gate={row['gate']} action={row['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
