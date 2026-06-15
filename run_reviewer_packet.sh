#!/usr/bin/env bash
set -u

LOG="reviewer_run.log"
: > "$LOG"

run_expect() {
  local expected="$1"
  shift
  echo ">>> $*" | tee -a "$LOG"
  "$@" > >(tee -a "$LOG") 2> >(tee -a "$LOG" >&2)
  local code=$?
  echo "<<< exit=$code expected=$expected" | tee -a "$LOG"
  echo "" | tee -a "$LOG"
  if [ "$code" -ne "$expected" ]; then
    echo "unexpected exit code for: $*" | tee -a "$LOG"
    return 1
  fi
  return 0
}

failures=0

run_expect 0 python3 -m unittest benchmarks/test_old_vs_new_benchmark.py || failures=$((failures + 1))
run_expect 0 python3 -m unittest curveballs/test_curveball_scenarios.py || failures=$((failures + 1))
run_expect 0 python3 -m unittest sensitivity/test_sensitivity_model.py || failures=$((failures + 1))
run_expect 0 python3 benchmarks/old_vs_new_benchmark.py || failures=$((failures + 1))
run_expect 0 python3 modeling/capacity_cost_model.py || failures=$((failures + 1))
run_expect 0 python3 modeling/migration_simulation.py || failures=$((failures + 1))
run_expect 0 python3 curveballs/curveball_scenarios.py || failures=$((failures + 1))
run_expect 0 python3 sensitivity/sensitivity_model.py || failures=$((failures + 1))
run_expect 1 python3 validation_harness/run_validation.py validation_harness/sample_events.jsonl || failures=$((failures + 1))
run_expect 0 python3 verify_packet.py || failures=$((failures + 1))

if [ "$failures" -ne 0 ]; then
  echo "reviewer replay failed: $failures unexpected command result(s)" | tee -a "$LOG"
  exit 1
fi

echo "reviewer replay passed; see $LOG" | tee -a "$LOG"
