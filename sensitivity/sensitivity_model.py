#!/usr/bin/env python3
"""Sensitivity sweep for scale, freshness, and budget cliffs."""

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MONTHLY_BUDGET = 50_000.0
BASE_EVENTS_PER_DAY = 50_000_000
SECONDS_PER_DAY = 86_400
GB_PER_MONTH_AT_1KB = BASE_EVENTS_PER_DAY * 30 / 1_000_000


@dataclass(frozen=True)
class Scenario:
    scenario: str
    spike_multiplier: float
    event_kb: float
    tenant_skew_pct: float
    late_event_pct: float
    export_write_amp: float
    stream_mbps: float
    freshness_seconds: float
    monthly_cost: float
    gate: str
    action: str


def classify_gate(
    stream_mbps: float,
    freshness_seconds: float,
    monthly_cost: float,
    tenant_skew_pct: float,
    late_event_pct: float,
    export_write_amp: float,
) -> str:
    if monthly_cost > MONTHLY_BUDGET or freshness_seconds > 30:
        return "fail"
    if tenant_skew_pct >= 25 or late_event_pct >= 10 or export_write_amp >= 5:
        return "manual_review"
    if stream_mbps > 25:
        return "manual_review"
    return "pass"


def estimate_scenario(
    name: str,
    spike_multiplier: float,
    event_kb: float,
    tenant_skew_pct: float,
    late_event_pct: float,
    export_write_amp: float,
    reserve_multiplier: float = 1.0,
) -> Scenario:
    events_per_second = BASE_EVENTS_PER_DAY / SECONDS_PER_DAY * spike_multiplier
    stream_mbps = events_per_second * event_kb / 1_024
    freshness_seconds = 3.5 + max(0, stream_mbps - 6) * 0.12 + late_event_pct * 0.35
    monthly_cost = (
        4_300
        + GB_PER_MONTH_AT_1KB * (event_kb - 1.0) * 0.025
        + spike_multiplier * 180
        + tenant_skew_pct * 85
        + late_event_pct * 120
        + export_write_amp * 650
    ) * reserve_multiplier
    gate = classify_gate(
        stream_mbps,
        freshness_seconds,
        monthly_cost,
        tenant_skew_pct,
        late_event_pct,
        export_write_amp,
    )
    action = {
        "pass": "eligible for cohort cutover after parity hold",
        "manual_review": "keep dual-write and require human go/no-go",
        "fail": "do not cut over; resize, reduce exports, or change architecture",
    }[gate]
    return Scenario(
        scenario=name,
        spike_multiplier=spike_multiplier,
        event_kb=event_kb,
        tenant_skew_pct=tenant_skew_pct,
        late_event_pct=late_event_pct,
        export_write_amp=export_write_amp,
        stream_mbps=round(stream_mbps, 2),
        freshness_seconds=round(freshness_seconds, 1),
        monthly_cost=round(monthly_cost, 2),
        gate=gate,
        action=action,
    )


def run_sweep() -> list[Scenario]:
    return [
        estimate_scenario("brief_peak", 10, 1.0, 2, 1, 1),
        estimate_scenario("large_payload_10x", 10, 8.0, 2, 1, 1),
        estimate_scenario("tenant_skew_35pct", 10, 1.0, 35, 1, 1),
        estimate_scenario("late_events_15pct", 10, 1.0, 2, 15, 1),
        estimate_scenario("export_write_amp_6x", 10, 1.0, 2, 1, 6),
        estimate_scenario("cost_ceiling_pressure", 20, 16.0, 35, 15, 8, reserve_multiplier=3.0),
    ]


def write_outputs(rows: list[Scenario]) -> None:
    csv_path = ROOT / "sensitivity_results.csv"
    report_path = ROOT / "sensitivity_report.md"
    trace_path = ROOT / "sensitivity_trace.log"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[f.name for f in fields(Scenario)])
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    lines = [
        "# Sensitivity Sweep Report",
        "",
        "This synthetic sweep names the scale, data-quality, and cost cliffs that would make the proposed architecture unsafe to cut over.",
        "",
        "| Scenario | Spike | Event KB | Tenant skew | Late events | Export amp | Stream MB/s | Freshness seconds | Monthly cost | Gate | Action |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.scenario} | [Assumed] {row.spike_multiplier}x | [Assumed] {row.event_kb} | "
            f"[Assumed] {row.tenant_skew_pct}% | [Assumed] {row.late_event_pct}% | "
            f"[Assumed] {row.export_write_amp}x | [Estimated] {row.stream_mbps} | "
            f"[Estimated] {row.freshness_seconds} | [Estimated] ${row.monthly_cost}/month | "
            f"{row.gate} | {row.action} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Takeaway",
            "",
            "The base design is not presented as infinitely elastic. Tenant skew, large payloads, late-event correction, export amplification, and reserve requirements are the explicit cliffs that trigger manual review or a failed cutover gate.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    trace_lines = ["sensitivity_model run"]
    for row in rows:
        trace_lines.append(
            f"{row.scenario} gate={row.gate} mbps={row.stream_mbps} "
            f"freshness={row.freshness_seconds}s cost=${row.monthly_cost}/month"
        )
    trace_path.write_text("\n".join(trace_lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = run_sweep()
    write_outputs(rows)
    print(f"wrote {len(rows)} sensitivity scenarios")
    for row in rows:
        print(
            f"{row.scenario}: gate={row.gate} mbps={row.stream_mbps} "
            f"freshness={row.freshness_seconds}s cost=${row.monthly_cost}/month"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
