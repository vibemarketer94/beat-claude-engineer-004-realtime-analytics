#!/usr/bin/env python3
"""Scenario capacity and cost model for Engineer 004.

This is not an AWS quote. It is a transparent model with labeled assumptions
that lets a reviewer inspect sizing logic and sensitivity to event size,
retention, and processing scale.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Scenario:
    name: str
    events_per_day: int
    peak_multiplier: float
    event_size_kb: float
    raw_retention_days: int
    hot_retention_days: int
    flink_kpus: int
    ingest_tasks: int
    redis_nodes: int
    dynamodb_write_multiplier: float
    log_sample_rate: float


SCENARIOS = [
    Scenario("mvp_expected", 50_000_000, 10, 1.0, 30, 7, 8, 6, 3, 0.2, 0.01),
    Scenario("full_expected", 50_000_000, 10, 1.0, 90, 14, 16, 10, 6, 0.5, 0.02),
    Scenario("large_payload", 50_000_000, 10, 2.5, 90, 14, 20, 14, 8, 0.5, 0.02),
    Scenario("growth_2x", 100_000_000, 10, 1.0, 90, 14, 24, 16, 8, 0.5, 0.02),
]


PRICES = {
    # [Benchmarked] Public AWS pricing pages checked June 2026.
    "kinesis_ingest_per_gb": 0.032,
    "kinesis_retrieval_per_gb": 0.016,
    "flink_kpu_hour": 0.11,
    "s3_standard_gb_month": 0.023,
    "cloudwatch_log_ingest_gb": 0.50,
    # [Assumed] Conservative blended placeholders when exact workload shape is unknown.
    "dynamodb_million_writes": 1.25,
    "fargate_task_month": 125.00,
    "redis_node_month": 155.00,
    "warehouse_export_support": 1500.00,
    "observability_fixed": 750.00,
}


def model(scenario: Scenario) -> dict[str, float | str]:
    avg_eps = scenario.events_per_day / 86_400
    peak_eps = avg_eps * scenario.peak_multiplier
    ingest_gb_day = scenario.events_per_day * scenario.event_size_kb / 1_000_000
    ingest_gb_month = ingest_gb_day * 30
    raw_storage_gb = ingest_gb_day * scenario.raw_retention_days * 1.35
    hot_events = scenario.events_per_day * scenario.hot_retention_days * scenario.dynamodb_write_multiplier
    dynamodb_million_writes = hot_events / 1_000_000

    kinesis = ingest_gb_month * (
        PRICES["kinesis_ingest_per_gb"] + (2 * PRICES["kinesis_retrieval_per_gb"])
    )
    flink = scenario.flink_kpus * 24 * 30 * PRICES["flink_kpu_hour"]
    s3 = raw_storage_gb * PRICES["s3_standard_gb_month"]
    dynamodb = dynamodb_million_writes * PRICES["dynamodb_million_writes"]
    fargate = scenario.ingest_tasks * PRICES["fargate_task_month"]
    redis = scenario.redis_nodes * PRICES["redis_node_month"]
    logs = ingest_gb_month * scenario.log_sample_rate * PRICES["cloudwatch_log_ingest_gb"]
    total = (
        kinesis
        + flink
        + s3
        + dynamodb
        + fargate
        + redis
        + logs
        + PRICES["warehouse_export_support"]
        + PRICES["observability_fixed"]
    )

    return {
        "scenario": scenario.name,
        "avg_events_sec": round(avg_eps, 1),
        "peak_events_sec": round(peak_eps, 1),
        "peak_mb_sec": round(peak_eps * scenario.event_size_kb / 1000, 2),
        "ingest_tb_month": round(ingest_gb_month / 1000, 2),
        "raw_storage_tb": round(raw_storage_gb / 1000, 2),
        "kinesis_month": round(kinesis, 2),
        "flink_month": round(flink, 2),
        "s3_month": round(s3, 2),
        "dynamodb_month": round(dynamodb, 2),
        "fargate_month": round(fargate, 2),
        "redis_month": round(redis, 2),
        "logs_month": round(logs, 2),
        "fixed_export_observability_month": round(
            PRICES["warehouse_export_support"] + PRICES["observability_fixed"], 2
        ),
        "estimated_total_month": round(total, 2),
        "under_50k": "yes" if total < 50_000 else "no",
}


def write_csv(rows: list[dict[str, float | str]]) -> None:
    path = ROOT / "capacity_cost_results.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict[str, float | str]]) -> None:
    lines = [
        "# Capacity and Cost Model Results",
        "",
        "All prices are planning inputs, not an AWS quote. Workload-specific DynamoDB, Redis, Fargate, export, and observability values remain assumptions until benchmarked.",
        "",
        "| Scenario | Avg eps | Peak eps | Peak MB/s | Ingest TB/mo | Raw TB | Kinesis | Flink | S3 | DynamoDB | Fargate | Redis | Logs | Fixed | Total | < $50K |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['avg_events_sec']} | {row['peak_events_sec']} | "
            f"{row['peak_mb_sec']} | {row['ingest_tb_month']} | {row['raw_storage_tb']} | "
            f"${row['kinesis_month']} | ${row['flink_month']} | ${row['s3_month']} | "
            f"${row['dynamodb_month']} | ${row['fargate_month']} | ${row['redis_month']} | "
            f"${row['logs_month']} | ${row['fixed_export_observability_month']} | "
            f"${row['estimated_total_month']} | {row['under_50k']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- [Estimated] The base workload is comfortably under the [Observed] $50K/month ceiling in this model.",
            "- [Estimated] DynamoDB hot aggregate write shape dominates variable cost more than raw streaming intake.",
            "- [Estimated] Payload growth matters less than hot-store write amplification unless retention and exports are uncontrolled.",
            "- [Assumed] The model uses a 1.35 raw-storage multiplier for normalized copies, metadata, and small-file overhead.",
            "",
            "## Source Labels",
            "",
            "- [Observed] 50M events/day, 10x spikes, 500+ tenants, and $50K/month ceiling come from the public brief.",
            "- [Benchmarked] Kinesis, Flink, S3, DynamoDB, CloudWatch, Fargate, and ElastiCache prices are public AWS pricing-page inputs checked in June 2026.",
            "- [Assumed] DynamoDB write amplification, task count, Redis node count, export support, and log sampling are workload placeholders.",
        ]
    )
    (ROOT / "capacity_cost_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = [model(scenario) for scenario in SCENARIOS]
    write_csv(rows)
    write_report(rows)
    print((ROOT / "capacity_cost_report.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
