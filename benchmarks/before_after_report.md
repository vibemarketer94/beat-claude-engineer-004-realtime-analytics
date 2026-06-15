# Before/After Benchmark Report

This is a synthetic before/after benchmark. It compares a broken current-pipeline model against a proposed-pipeline model using the same accepted-event workload and a declared method.

| Scenario | Events | Old loss | New loss | Loss improvement | Old dupes | New dupes | Dupe improvement | Old p95 freshness | New p95 freshness | Freshness improvement | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| peak_expected | 50000 | 3.032% | 0.088% | 97.1% | 0.567% | 0.27% | 52.36% | 1320s | 4.2s | 99.68% | pass |
| black_friday_spike | 200000 | 3.009% | 0.148% | 95.06% | 0.905% | 0.394% | 56.5% | 1800s | 4.8s | 99.73% | pass |
| proposed_regression | 50000 | 2.902% | 1.228% | 57.68% | 0.54% | 1.079% | -99.99% | 1320s | 8.0s | 99.39% | fail |

## Method

- [Observed] Current pipeline peak loss is modeled from the public brief's about 3% event loss.
- [Observed] Current dashboard freshness is modeled from the public brief's 15-30 minute latency range.
- [Estimated] Proposed loss, duplicate, and freshness values are candidate SLO targets tested by the benchmark.
- [Estimated] Proposed cutover gate fails when new loss exceeds 0.5%, duplicates exceed 0.5%, or p95 freshness exceeds 5 seconds.

## Tier 4 Claim

This supports Tier 4 as synthetic before/after benchmark evidence: measured change with a clear benchmark and method. It is not Tier 5 and not production before/after data.
