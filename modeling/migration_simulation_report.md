# Migration Simulation Results

This simulation scales the migration problem down to synthetic dual-write cohorts. It does not claim production proof; it demonstrates the gates and failure behavior.

| Scenario | Events | Old seen | New seen | Old loss | New loss | Old/new delta | Duplicate % | Late % | Freshness p95 | Worst tenant delta | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| baseline_current | 50000 | 48484 | 49958 | 3.032% | 0.084% | 2.948% | 0.25% | 0.966% | 3.8s | 50 | yes |
| black_friday_spike | 200000 | 194040 | 199599 | 2.98% | 0.2% | 2.78% | 0.59% | 2.982% | 4.7s | 149 | no |
| new_pipeline_regression | 50000 | 48527 | 49406 | 2.946% | 1.188% | 1.758% | 0.982% | 1.936% | 6.4s | 34 | no |

## Gate Logic

- [Estimated] New-path loss against accepted intake must be <= 0.5%.
- [Estimated] Duplicate rate must be <= 0.5%.
- [Observed target] Freshness p95 must be <= 5 seconds.
- [Estimated] Worst tenant old/new count delta must be <= 75 events in the synthetic cohort.

## Interpretation

- [Observed] The current-path 3% loss from the brief creates a baseline comparison problem; new-path gates should compare against accepted intake, not blindly match broken old counts.
- [Estimated] The spike scenario can pass if new-path loss, duplicates, and freshness stay within gates.
- [Estimated] The regression scenario fails because freshness and parity gates catch it before cutover.
