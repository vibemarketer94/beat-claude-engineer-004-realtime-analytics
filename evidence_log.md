# Evidence Log

This log uses the public `SCORING.md` tiers literally. The packet has Tier 2 demo artifacts, Tier 3 generated logs/source records, and a synthetic Tier 4 before/after benchmark (measured change with a clear method, not production data). The reviewer replay is reproduced in a clean environment by GitHub Actions, but no external human or customer has confirmed the result, so no Tier 5 human verification is claimed.

Note on labels: `[Observed synthetic]` is a sub-label of the four public labels — it means a figure observed from a runnable synthetic model rather than a production system. For source-label purposes it is treated as `[Estimated]`; it is called out only to be explicit that the number comes from an inspectable benchmark, not production.

| Claim | Source Label | Proof Tier | Evidence Type | Artifact | Why This Tier | Limitation |
|---|---|---:|---|---|---|---|
| Brief requires about 50M events/day. | [Observed] | 3 | Source record | Public Engineer 004 brief | The public brief is the source record for the task constraint. | Challenge-provided figure, not our production log. |
| Brief requires less than 5 second visibility. | [Observed] | 3 | Source record | Public Engineer 004 brief | The public brief is the source record for the task constraint. | Requirement, not measured behavior. |
| Brief states current system loses about 3% during peaks. | [Observed] | 3 | Source record | Public Engineer 004 brief | The public brief is the source record for the task constraint. | Challenge-provided figure. |
| Average traffic is about 579 events/sec. | [Estimated] | 2 | Demo artifact | `cost_model.md`, `modeling/capacity_cost_model.py` | Derived in a reviewable model. | Uses 30-day simplification and brief volume. |
| 10x peak traffic is about 5,790 events/sec. | [Estimated] | 2 | Demo artifact | `cost_model.md`, `modeling/capacity_cost_model.py` | Derived in a reviewable model. | Uses challenge peak multiplier. |
| Kinesis can fit this workload with room for peak ingest in supported regions. | [Benchmarked] | 3 | Source record | AWS Kinesis quotas link in `cost_model.md` | Public AWS quota docs are source records. | Must verify target region and account limits. |
| Packet cost posture can remain below $50K/month. | [Estimated] | 2 | Demo artifact | `cost_model.md`, `modeling/capacity_cost_report.md` | Scenario model is inspectable and rerunnable. | Depends on event size, retention, hot-store writes, exports, and logging volume. |
| Proposed design improves synthetic peak expected loss from 3.032% to 0.088%. | [Observed synthetic] | 4 | Before/after benchmark | `benchmarks/before_after_report.md`, `benchmarks/before_after_results.csv` | Measured change with a clear benchmark and method. | Synthetic benchmark, not production data. |
| Proposed design improves synthetic p95 freshness from 1,320 seconds to 4.2 seconds. | [Observed synthetic] | 4 | Before/after benchmark | `benchmarks/before_after_report.md`, `benchmarks/before_after_results.csv` | Measured change with a clear benchmark and method. | Synthetic benchmark, not production data. |
| Generated capacity/cost scenarios estimate $4.3K-$8.8K/month for modeled core paths. | [Estimated] | 3 | Generated log/source record | `modeling/capacity_cost_trace.log`, `modeling/capacity_cost_results.csv` | Generated trace and CSV record the model run. | Model uses assumptions; not an AWS quote. |
| Before/after benchmark trace was generated. | [Observed] | 3 | Generated log | `benchmarks/before_after_trace.log` | Local run output records the benchmark. | Not independent verification. |
| Before/after benchmark tests pass. | [Observed] | 3 | Test output | `benchmarks/test_old_vs_new_benchmark.py`, `verification_report.md` | Packet verifier runs the test suite. | Local test execution only. |
| Curveball scenarios cover six likely private-review failure modes. | [Observed synthetic] | 2 | Demo artifact | `curveballs/curveball_report.md`, `curveballs/curveball_results.csv` | Runnable artifact demonstrates operating decisions for bad inputs, compliance conflicts, and traffic pressure. | Synthetic scenarios, not production incidents. |
| Curveball tests pass and generated trace records fail/manual-review gates. | [Observed] | 3 | Test output and generated log | `curveballs/test_curveball_scenarios.py`, `curveballs/curveball_trace.log`, `verification_report.md` | Packet verifier runs the tests and script. | Local test execution only. |
| Sensitivity sweep covers six scale and budget cliff scenarios. | [Observed synthetic] | 2 | Demo artifact | `sensitivity/sensitivity_report.md`, `sensitivity/sensitivity_results.csv` | Runnable model names when cutover passes, needs manual review, or fails. | Synthetic model, not measured AWS load test. |
| Sensitivity tests pass and generated trace records a budget fail gate. | [Observed] | 3 | Test output and generated log | `sensitivity/test_sensitivity_model.py`, `sensitivity/sensitivity_trace.log`, `verification_report.md` | Packet verifier runs the tests and script. | Local test execution only. |
| Reviewer replay runs tests, scripts, validation, and packet verification from one command. | [Observed] | 3 | Generated log | `run_reviewer_packet.sh`, `reviewer_run.log` | Replay log records command output and expected exit codes. | Local replay only unless run by CI or reviewer. |
| Reviewer replay reproduces in a clean environment. | [Observed] | 3 | CI run record | `.github/workflows/reviewer-replay.yml`, GitHub Actions run history | GitHub Actions runs the full replay on every push and is green. | Machine reproduction, not human/customer verification; not Tier 5. |
| Validation harness detects duplicates, missing sequences, and parity mismatch. | [Observed] | 2 | Demo artifact | `validation_harness/run_validation.py`, `validation_harness/sample_events.jsonl` | Runnable artifact demonstrates behavior. | Synthetic proof only. |
| Local validation harness trace was generated. | [Observed] | 3 | Generated log | `validation_harness/validation_trace.log` | Local run output records the result. | Not independent verification. |
| Migration gates catch a new-pipeline regression before cutover. | [Observed] | 2 | Demo artifact | `modeling/migration_simulation.py`, `modeling/migration_simulation_report.md` | Runnable simulation demonstrates the gate. | Synthetic simulation only. |
| Local migration simulation trace was generated. | [Observed] | 3 | Generated log | `modeling/migration_simulation_trace.log` | Local run output records the result. | Not production proof. |
| Migration should use dual-write and shadow validation before cutover. | [Estimated] | 2 | Process artifact | `migration_runbook.md` | Runbook is an inspectable operating artifact. | Operating judgment based on risk, not production trial. |
| Deletion must propagate across hot store, cold lake, cache, and exports. | [Estimated] | 2 | Design artifact | `architecture.mmd`, `validation_plan.md` | Diagram and test plan are inspectable artifacts. | Exact implementation depends on storage choices. |

## Evidence Tier Summary

| Tier | Present? | Packet Evidence |
|---|---|---|
| 0 Claims only | Avoided for major claims | Claims are linked to artifacts, source records, or assumptions. |
| 1 Screenshots | No | Not needed; generated logs are stronger than screenshots for this packet. |
| 2 Demo artifact | Yes | Scripts, model reports, curveball scenarios, sensitivity sweep, diagram, runbook, test plan. |
| 3 Logs or source records | Yes | Public brief, AWS docs, generated trace logs, reviewer replay log, CSV outputs. |
| 4 Before/after data | Yes, synthetic | `benchmarks/before_after_report.md` measures before/after change with a clear method. |
| 5 Independent verification | No | No external reviewer/system has verified the packet. |
