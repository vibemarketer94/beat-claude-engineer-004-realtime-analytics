#!/usr/bin/env python3
"""Synthetic validation harness for Engineer 004.

The harness is intentionally small: it demonstrates dedupe, tenant isolation,
sequence-gap detection, and old/new parity gates without needing cloud
credentials or private data.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


PASS_WITH_WARNINGS_CASES = {"messy"}


def load_events(path: Path) -> list[dict]:
    events: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON on line {line_number}: {exc}") from exc
    return events


def validate_case(case: str, events: list[dict]) -> dict:
    seen: set[tuple[str, str]] = set()
    duplicates: list[str] = []
    unique_events: list[dict] = []
    sequences_by_tenant_user: dict[tuple[str, str], list[int]] = defaultdict(list)
    old_expected_values = {event.get("old_pipeline_expected") for event in events}

    for event in events:
        key = (event["tenant_id"], event["event_id"])
        if key in seen:
            duplicates.append(f"{event['tenant_id']}:{event['event_id']}")
            continue
        seen.add(key)
        unique_events.append(event)
        actor = event.get("user_id") or event.get("anonymous_id") or "unknown"
        sequences_by_tenant_user[(event["tenant_id"], actor)].append(int(event["sequence"]))

    missing_sequences: list[str] = []
    for (tenant_id, actor), sequences in sequences_by_tenant_user.items():
        ordered = sorted(sequences)
        if not ordered:
            continue
        expected = set(range(ordered[0], ordered[-1] + 1))
        missing = sorted(expected - set(ordered))
        if missing:
            missing_sequences.append(f"{tenant_id}:{actor} missing {missing}")

    old_expected = old_expected_values.pop() if len(old_expected_values) == 1 else None
    parity_ok = old_expected == len(unique_events)
    warnings = []
    if duplicates:
        warnings.append(f"duplicates={len(duplicates)}")
    if missing_sequences:
        warnings.append(f"missing_sequences={len(missing_sequences)}")
    if not parity_ok:
        warnings.append(f"parity_mismatch old={old_expected} new={len(unique_events)}")

    pass_gate = parity_ok and not missing_sequences
    if case in PASS_WITH_WARNINGS_CASES:
        pass_gate = parity_ok and not missing_sequences

    return {
        "case": case,
        "input_events": len(events),
        "unique_events": len(unique_events),
        "duplicates": duplicates,
        "missing_sequences": missing_sequences,
        "old_expected": old_expected,
        "parity_ok": parity_ok,
        "pass_gate": pass_gate,
        "warnings": warnings,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: run_validation.py sample_events.jsonl", file=sys.stderr)
        return 2

    events = load_events(Path(sys.argv[1]))
    by_case: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_case[event["case"]].append(event)

    overall_ok = True
    for case in sorted(by_case):
        result = validate_case(case, by_case[case])
        status = "PASS" if result["pass_gate"] else "FAIL"
        if not result["pass_gate"]:
            overall_ok = False
        print(
            f"{status} case={case} input={result['input_events']} "
            f"unique={result['unique_events']} old_expected={result['old_expected']} "
            f"parity_ok={result['parity_ok']}"
        )
        for warning in result["warnings"]:
            print(f"  warning: {warning}")
        for missing in result["missing_sequences"]:
            print(f"  review: {missing}")
        if not result["pass_gate"]:
            print("  action: hold rollout and require human review")

    print(f"OVERALL {'PASS' if overall_ok else 'FAIL_REQUIRES_REVIEW'}")
    return 1 if not overall_ok else 0


if __name__ == "__main__":
    raise SystemExit(main())

