#!/usr/bin/env python3
"""Verify the Engineer 004 packet against public submission requirements."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LABELS = ("[Observed]", "[Estimated]", "[Benchmarked]", "[Assumed]")

REQUIRED_FILES = [
    "ENGINEER_004_SUBMISSION_READY.md",
    "README.md",
    "submission.md",
    "architecture.mmd",
    "cost_model.md",
    "event_contract.md",
    "migration_runbook.md",
    "validation_plan.md",
    "evidence_log.md",
    "reviewer_scorecard.md",
    "challenge_requirements_matrix.md",
    "operating_artifact.md",
    "ai_usage.md",
    "walkthrough.md",
    "run_reviewer_packet.sh",
    "reviewer_run.log",
    "validation_harness/README.md",
    "validation_harness/sample_events.jsonl",
    "validation_harness/run_validation.py",
    "validation_harness/expected_output.md",
    "modeling/capacity_cost_model.py",
    "modeling/migration_simulation.py",
    "modeling/capacity_cost_report.md",
    "modeling/capacity_cost_results.csv",
    "modeling/capacity_cost_trace.log",
    "modeling/migration_simulation_report.md",
    "modeling/migration_simulation_results.csv",
    "modeling/migration_simulation_trace.log",
    "validation_harness/validation_trace.log",
    "benchmarks/old_vs_new_benchmark.py",
    "benchmarks/test_old_vs_new_benchmark.py",
    "benchmarks/before_after_report.md",
    "benchmarks/before_after_results.csv",
    "benchmarks/before_after_trace.log",
    "curveballs/curveball_scenarios.py",
    "curveballs/test_curveball_scenarios.py",
    "curveballs/curveball_report.md",
    "curveballs/curveball_results.csv",
    "curveballs/curveball_trace.log",
    "sensitivity/sensitivity_model.py",
    "sensitivity/test_sensitivity_model.py",
    "sensitivity/sensitivity_report.md",
    "sensitivity/sensitivity_results.csv",
    "sensitivity/sensitivity_trace.log",
]

BRIEF_REQUIREMENTS = [
    "50M",
    "10x",
    "5 second",
    "AWS",
    "SDK",
    "500+",
    "SOC 2",
    "GDPR",
    "CCPA",
    "Snowflake",
    "BigQuery",
    "rollback",
    "validate",
    "warehouse",
    "personalization",
    "segment",
    "identity",
    "stitching",
    "trade-off",
    "risk",
    "zero data loss",
]

MATRIX_REQUIREMENTS = [
    "High-level system diagram",
    "Technology/services",
    "Event data structure",
    "identity/stitching",
    "50M+ events/day",
    "10x spikes",
    "Zero data loss",
    "Rollback plan",
    "Validate data accuracy",
    "Trade-offs and risks",
    "No SDK breaking change",
    "Written answer",
    "Operating artifact",
    "Evidence log",
    "Number source labels",
    "AI usage disclosure",
    "What breaks it",
    "What stays human",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def result(ok: bool, name: str, detail: str) -> tuple[bool, str]:
    status = "PASS" if ok else "FAIL"
    return ok, f"{status}: {name} - {detail}"


def check_required_files() -> list[tuple[bool, str]]:
    rows = []
    for rel in REQUIRED_FILES:
        rows.append(result((ROOT / rel).is_file(), f"required file {rel}", "present"))
    return rows


def check_submission_length() -> tuple[bool, str]:
    words = len(re.findall(r"\S+", read("submission.md")))
    ready_words = len(re.findall(r"\S+", read("ENGINEER_004_SUBMISSION_READY.md")))
    return result(
        words <= 1800 and ready_words <= 2200,
        "submission length",
        f"short answer {words} words <= 1800; upload file {ready_words} words <= 2200 proxy",
    )


def check_brief_coverage() -> list[tuple[bool, str]]:
    corpus = "\n".join(
        read(path)
        for path in [
            "submission.md",
            "architecture.mmd",
            "migration_runbook.md",
            "validation_plan.md",
            "cost_model.md",
        ]
    ).lower()
    rows = []
    for term in BRIEF_REQUIREMENTS:
        rows.append(result(term.lower() in corpus, f"brief coverage {term}", "mentioned in packet"))
    return rows


def check_matrix_coverage() -> list[tuple[bool, str]]:
    matrix = read("challenge_requirements_matrix.md").lower()
    return [
        result(term.lower() in matrix, f"matrix coverage {term}", "mapped in challenge requirements matrix")
        for term in MATRIX_REQUIREMENTS
    ]


def check_number_labels() -> list[tuple[bool, str]]:
    rows = []
    number_pattern = re.compile(r"(?<![A-Za-z])(?:\$?\d[\d,]*(?:\.\d+)?(?:K|M|x|%| TB| GB| KB| seconds?| days?|/month|/day|/sec)?)")
    skip_patterns = (
        re.compile(r"^\s*#"),
        re.compile(r"^\s*\|?[-: ]+\|"),
        re.compile(r"^\s*[-*]?\s*https?://"),
        re.compile(r"^\s*-\s+.*https?://"),
        re.compile(r"https?://"),
        re.compile(r"^\s*\|.*Proof Tier.*\|"),
        re.compile(r"^\s*\|.*\bSource\b.*\|"),
        re.compile(r"^\s*\|.*\bSource Label\b.*\|"),
        re.compile(r"^\s*\|.*\[[A-Za-z ]+\].*\|"),
        re.compile(r"^\s*\d+\.\s+"),
        re.compile(r"^Proof tiers follow"),
        re.compile(r"SOC 2"),
        re.compile(r"Evidence tiers present"),
        re.compile(r"`[^`]+`"),
        re.compile(r"^\|\s*[0-5]\s+"),
    )
    for rel in ["ENGINEER_004_SUBMISSION_READY.md", "submission.md", "cost_model.md", "evidence_log.md"]:
        for line_no, line in enumerate(read(rel).splitlines(), start=1):
            if any(pattern.search(line) for pattern in skip_patterns):
                continue
            if number_pattern.search(line) and not any(label in line for label in LABELS):
                rows.append(result(False, f"number label {rel}:{line_no}", line.strip()))
    if not rows:
        rows.append(result(True, "number labels", "all scanned numeric claim lines include source labels"))
    return rows


def check_harness() -> list[tuple[bool, str]]:
    proc = subprocess.run(
        [sys.executable, "validation_harness/run_validation.py", "validation_harness/sample_events.jsonl"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    expected = read("validation_harness/expected_output.md").split("```text\n", 1)[1].split("\n```", 1)[0]
    rows = [
        result(proc.returncode == 1, "harness exit code", f"exit code {proc.returncode}; failure case should require review"),
        result(proc.stdout.strip() == expected.strip(), "harness expected output", "stdout matches expected_output.md"),
        result("PASS case=normal" in proc.stdout, "harness normal case", "normal case passes"),
        result("PASS case=messy" in proc.stdout, "harness messy case", "messy case passes with duplicate warning"),
        result("FAIL case=failure" in proc.stdout, "harness failure case", "failure case fails"),
        result("human review" in proc.stdout, "harness human review", "failure routes to human review"),
    ]
    if proc.stderr:
        rows.append(result(False, "harness stderr", proc.stderr.strip()))
    return rows


def check_modeling() -> list[tuple[bool, str]]:
    rows: list[tuple[bool, str]] = []
    for script in ["modeling/capacity_cost_model.py", "modeling/migration_simulation.py"]:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        rows.append(result(proc.returncode == 0, f"model {script}", "script runs successfully"))
        if proc.stderr:
            rows.append(result(False, f"model stderr {script}", proc.stderr.strip()))

    cost_report = read("modeling/capacity_cost_report.md")
    migration_report = read("modeling/migration_simulation_report.md")
    rows.append(result("growth_2x" in cost_report, "capacity model growth scenario", "2x growth scenario present"))
    rows.append(result("< $50K" in cost_report, "capacity model ceiling", "50K ceiling column present"))
    rows.append(result("new_pipeline_regression" in migration_report, "migration regression scenario", "regression scenario present"))
    rows.append(result("| new_pipeline_regression" in migration_report and "| no |" in migration_report, "migration failure gate", "regression fails gate"))
    rows.append(result("growth_2x" in read("modeling/capacity_cost_trace.log"), "capacity trace", "generated trace includes growth scenario"))
    rows.append(result("new_pipeline_regression" in read("modeling/migration_simulation_trace.log"), "migration trace", "generated trace includes regression scenario"))
    rows.append(result("FAIL_REQUIRES_REVIEW" in read("validation_harness/validation_trace.log"), "validation trace", "generated trace includes expected failure gate"))
    return rows


def check_before_after_benchmark() -> list[tuple[bool, str]]:
    rows: list[tuple[bool, str]] = []
    test_proc = subprocess.run(
        [sys.executable, "-m", "unittest", "benchmarks/test_old_vs_new_benchmark.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    bench_proc = subprocess.run(
        [sys.executable, "benchmarks/old_vs_new_benchmark.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    (ROOT / "benchmarks/before_after_trace.log").write_text(bench_proc.stdout, encoding="utf-8")
    rows.append(result(test_proc.returncode == 0, "before/after tests", "unit tests pass"))
    if test_proc.stderr and "OK" not in test_proc.stderr:
        rows.append(result(False, "before/after test stderr", test_proc.stderr.strip()))
    rows.append(result(bench_proc.returncode == 0, "before/after benchmark", "script runs successfully"))
    report = read("benchmarks/before_after_report.md")
    rows.append(result("Tier 4" in report, "before/after tier 4 note", "report explains synthetic Tier 4 claim"))
    rows.append(result("97.1%" in report, "before/after loss delta", "peak expected loss improvement present"))
    rows.append(result("99.68%" in report, "before/after freshness delta", "peak expected freshness improvement present"))
    rows.append(result("proposed_regression" in report and "| fail |" in report, "before/after regression gate", "regression scenario fails"))
    return rows


def check_curveballs_and_sensitivity() -> list[tuple[bool, str]]:
    rows: list[tuple[bool, str]] = []
    commands = [
        ("curveball tests", [sys.executable, "-m", "unittest", "curveballs/test_curveball_scenarios.py"]),
        ("sensitivity tests", [sys.executable, "-m", "unittest", "sensitivity/test_sensitivity_model.py"]),
        ("curveball scenarios", [sys.executable, "curveballs/curveball_scenarios.py"]),
        ("sensitivity model", [sys.executable, "sensitivity/sensitivity_model.py"]),
    ]
    for name, command in commands:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        rows.append(result(proc.returncode == 0, name, "command runs successfully"))
        if proc.stderr and "OK" not in proc.stderr:
            rows.append(result(False, f"{name} stderr", proc.stderr.strip()))

    curveball_report = read("curveballs/curveball_report.md")
    sensitivity_report = read("sensitivity/sensitivity_report.md")
    curveball_trace = read("curveballs/curveball_trace.log")
    sensitivity_trace = read("sensitivity/sensitivity_trace.log")

    rows.append(result("tenant_hotspot" in curveball_report, "curveball tenant hotspot", "private-review curveball present"))
    rows.append(result("gdpr_delete_during_replay" in curveball_report, "curveball deletion replay", "compliance curveball present"))
    rows.append(result("warehouse_export_failure" in curveball_report, "curveball export failure", "warehouse curveball present"))
    rows.append(result("cost_ceiling_pressure" in sensitivity_report, "sensitivity cost cliff", "budget cliff present"))
    rows.append(result("manual_review" in sensitivity_report, "sensitivity manual review gate", "manual-review gates present"))
    rows.append(result("gate=fail" in sensitivity_trace, "sensitivity fail gate trace", "failing scenario recorded"))
    rows.append(result("gate=fail" in curveball_trace, "curveball fail gate trace", "failing curveball recorded"))
    return rows


def check_sources() -> list[tuple[bool, str]]:
    cost = read("cost_model.md")
    required = [
        "aws.amazon.com/kinesis/data-streams/pricing",
        "docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits",
        "aws.amazon.com/managed-service-apache-flink/pricing",
        "aws.amazon.com/s3/pricing",
    ]
    return [result(source in cost, f"source {source}", "present in cost model") for source in required]


def main() -> int:
    checks: list[tuple[bool, str]] = []
    checks.extend(check_required_files())
    checks.append(check_submission_length())
    checks.extend(check_brief_coverage())
    checks.extend(check_matrix_coverage())
    checks.extend(check_number_labels())
    checks.extend(check_harness())
    checks.extend(check_modeling())
    checks.extend(check_before_after_benchmark())
    checks.extend(check_curveballs_and_sensitivity())
    checks.extend(check_sources())

    report = "# Packet Verification Report\n\n" + "\n".join(f"- {line}" for _, line in checks) + "\n"
    (ROOT / "verification_report.md").write_text(report, encoding="utf-8")
    print(report)

    return 0 if all(ok for ok, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
