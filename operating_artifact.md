# Operating Artifact

This packet includes a repo-style engineering operating artifact, not only a written answer.

## What to Inspect

| Artifact Type | File | What it proves |
|---|---|---|
| Architecture diagram | `architecture.mmd` | Data flow from SDK to dashboard, personalization, export, deletion, and observability. |
| Runnable validation script | `validation_harness/run_validation.py` | Dedupe, sequence-gap detection, parity failure, and human-review routing on synthetic events. |
| Test data | `validation_harness/sample_events.jsonl` | Normal, messy, and failure/ambiguous cases. |
| Expected validation trace | `validation_harness/expected_output.md` | Known-good output for the runnable harness. |
| Generated validation trace | `validation_harness/validation_trace.log` | Actual local run output from the harness. |
| Benchmark/model script | `modeling/capacity_cost_model.py` | Scenario-based capacity and cost sensitivity model. |
| Benchmark report | `modeling/capacity_cost_report.md` | Generated cost/capacity results for MVP, full, large-payload, and growth scenarios. |
| Benchmark CSV | `modeling/capacity_cost_results.csv` | Machine-readable model output. |
| Benchmark trace | `modeling/capacity_cost_trace.log` | Actual local run output from the capacity/cost model. |
| Before/after benchmark script | `benchmarks/old_vs_new_benchmark.py` | Synthetic current-vs-proposed benchmark for Tier 4-style evidence. |
| Before/after benchmark tests | `benchmarks/test_old_vs_new_benchmark.py` | Unit tests for improvement and regression-gate behavior. |
| Before/after report | `benchmarks/before_after_report.md` | Measured before/after loss, duplicate, and freshness deltas. |
| Before/after CSV | `benchmarks/before_after_results.csv` | Machine-readable benchmark output. |
| Before/after trace | `benchmarks/before_after_trace.log` | Actual local run output from the benchmark. |
| Curveball script | `curveballs/curveball_scenarios.py` | Private-review-style operating decisions for hotspots, bad SDK payloads, deletion during replay, export failure, backpressure, and clock skew. |
| Curveball tests | `curveballs/test_curveball_scenarios.py` | Regression tests that enforce safe operating actions for failure-mode scenarios. |
| Curveball report/CSV/trace | `curveballs/curveball_report.md`, `curveballs/curveball_results.csv`, `curveballs/curveball_trace.log` | Reviewer-readable and machine-readable results for hidden-benchmark-style scenarios. |
| Sensitivity model | `sensitivity/sensitivity_model.py` | Synthetic sweep over payload size, spike size, tenant skew, late events, export amplification, and budget pressure. |
| Sensitivity tests | `sensitivity/test_sensitivity_model.py` | Regression tests that enforce cliff-edge gates. |
| Sensitivity report/CSV/trace | `sensitivity/sensitivity_report.md`, `sensitivity/sensitivity_results.csv`, `sensitivity/sensitivity_trace.log` | Reviewer-readable and machine-readable results for scale and cost cliffs. |
| Migration simulation script | `modeling/migration_simulation.py` | Synthetic dual-write migration gate simulation. |
| Migration simulation report | `modeling/migration_simulation_report.md` | Generated baseline, spike, and regression gate results. |
| Migration simulation CSV | `modeling/migration_simulation_results.csv` | Machine-readable migration simulation output. |
| Migration trace | `modeling/migration_simulation_trace.log` | Actual local run output from the migration simulation. |
| Reviewer replay | `run_reviewer_packet.sh`, `reviewer_run.log` | One-command replay of tests, models, validation, and packet verification. |
| Live walkthrough | `walkthrough.md` | Short reviewer script for live explanation and curveball follow-up. |
| Test plan | `validation_plan.md` | Production validation gates and response playbook. |
| Evidence log | `evidence_log.md` | Claims mapped to source labels and proof tiers. |

## How to Run

Run from `engineer-004-packet/`:

```bash
./run_reviewer_packet.sh
python3 validation_harness/run_validation.py validation_harness/sample_events.jsonl
python3 -m unittest benchmarks/test_old_vs_new_benchmark.py
python3 -m unittest curveballs/test_curveball_scenarios.py
python3 -m unittest sensitivity/test_sensitivity_model.py
python3 benchmarks/old_vs_new_benchmark.py
python3 modeling/capacity_cost_model.py
python3 modeling/migration_simulation.py
python3 curveballs/curveball_scenarios.py
python3 sensitivity/sensitivity_model.py
python3 verify_packet.py
```

The validation harness intentionally exits with code `1` because the sample includes a failure case. That is expected: the artifact should prove that bad migration data fails the gate and routes to human review.

## What Counts as "Works"

- The validation harness detects duplicates, missing sequences, parity mismatch, and human-review cases.
- The before/after benchmark measures improvement against a declared broken-current-pipeline baseline.
- The capacity model generates scenario outputs and keeps source-labeled assumptions visible.
- The migration simulation catches a new-pipeline regression before cutover.
- The curveball scenarios show reviewer-follow-up failure handling instead of generic incident prose.
- The sensitivity sweep names scale, data-quality, and budget cliffs that require manual review or failed cutover.
- `verify_packet.py` reruns the scripts and records the packet verification result in `verification_report.md`.
