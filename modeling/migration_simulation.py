#!/usr/bin/env python3
"""Synthetic dual-write migration simulation for Engineer 004."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Scenario:
    name: str
    tenants: int
    events: int
    old_loss_rate: float
    new_loss_rate: float
    duplicate_rate: float
    late_rate: float
    freshness_p95_sec: float
    seed: int


# Each scenario carries its own seed so results are reproducible and independent
# of evaluation order (a reviewer re-running any scenario sees the same numbers).
SCENARIOS = [
    Scenario("baseline_current", 50, 50_000, 0.03, 0.001, 0.003, 0.01, 3.8, 42),
    Scenario("black_friday_spike", 50, 200_000, 0.03, 0.002, 0.006, 0.03, 4.7, 43),
    Scenario("new_pipeline_regression", 50, 50_000, 0.03, 0.012, 0.010, 0.02, 6.4, 44),
]


def simulate(scenario: Scenario) -> dict[str, float | str]:
    rng = random.Random(scenario.seed)
    intake_accepted = scenario.events
    old_seen = 0
    new_seen = 0
    duplicates = 0
    late = 0
    tenant_deltas: dict[str, int] = {f"tenant_{i:03d}": 0 for i in range(scenario.tenants)}

    for i in range(scenario.events):
        tenant = f"tenant_{i % scenario.tenants:03d}"
        old_ok = rng.random() >= scenario.old_loss_rate
        new_ok = rng.random() >= scenario.new_loss_rate
        if old_ok:
            old_seen += 1
            tenant_deltas[tenant] += 1
        if new_ok:
            new_seen += 1
            tenant_deltas[tenant] -= 1
            if rng.random() < scenario.duplicate_rate:
                duplicates += 1
        if rng.random() < scenario.late_rate:
            late += 1

    old_loss_pct = (intake_accepted - old_seen) / max(intake_accepted, 1)
    new_loss_pct = (intake_accepted - new_seen) / max(intake_accepted, 1)
    old_new_delta_pct = abs(old_seen - new_seen) / max(intake_accepted, 1)
    duplicate_pct = duplicates / max(new_seen, 1)
    late_pct = late / scenario.events
    worst_tenant_delta = max(abs(delta) for delta in tenant_deltas.values())
    pass_gate = (
        new_loss_pct <= 0.005
        and duplicate_pct <= 0.005
        and scenario.freshness_p95_sec <= 5.0
        and worst_tenant_delta <= 75
    )

    return {
        "scenario": scenario.name,
        "input_events": scenario.events,
        "old_seen": old_seen,
        "new_seen": new_seen,
        "old_loss_pct": round(old_loss_pct * 100, 3),
        "new_loss_pct": round(new_loss_pct * 100, 3),
        "old_new_delta_pct": round(old_new_delta_pct * 100, 3),
        "duplicate_pct": round(duplicate_pct * 100, 3),
        "late_pct": round(late_pct * 100, 3),
        "freshness_p95_sec": scenario.freshness_p95_sec,
        "worst_tenant_delta": worst_tenant_delta,
        "pass_gate": "yes" if pass_gate else "no",
    }


def write_csv(rows: list[dict[str, float | str]]) -> None:
    path = ROOT / "migration_simulation_results.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict[str, float | str]]) -> None:
    lines = [
        "# Migration Simulation Results",
        "",
        "This simulation scales the migration problem down to synthetic dual-write cohorts. It does not claim production proof; it demonstrates the gates and failure behavior.",
        "",
        "| Scenario | Events | Old seen | New seen | Old loss | New loss | Old/new delta | Duplicate % | Late % | Freshness p95 | Worst tenant delta | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['input_events']} | {row['old_seen']} | {row['new_seen']} | "
            f"{row['old_loss_pct']}% | {row['new_loss_pct']}% | {row['old_new_delta_pct']}% | "
            f"{row['duplicate_pct']}% | {row['late_pct']}% | "
            f"{row['freshness_p95_sec']}s | {row['worst_tenant_delta']} | {row['pass_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Gate Logic",
            "",
            "- [Estimated] New-path loss against accepted intake must be <= 0.5%.",
            "- [Estimated] Duplicate rate must be <= 0.5%.",
            "- [Observed target] Freshness p95 must be <= 5 seconds.",
            "- [Estimated] Worst tenant old/new count delta must be <= 75 events in the synthetic cohort.",
            "",
            "## Interpretation",
            "",
            "- [Observed] The current-path 3% loss from the brief creates a baseline comparison problem; new-path gates should compare against accepted intake, not blindly match broken old counts.",
            "- [Estimated] The spike scenario can pass if new-path loss, duplicates, and freshness stay within gates.",
            "- [Estimated] The regression scenario fails because freshness and parity gates catch it before cutover.",
        ]
    )
    (ROOT / "migration_simulation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = [simulate(scenario) for scenario in SCENARIOS]
    write_csv(rows)
    write_report(rows)
    print((ROOT / "migration_simulation_report.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
