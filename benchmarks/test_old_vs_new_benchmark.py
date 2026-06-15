#!/usr/bin/env python3
"""Tests for the synthetic before/after benchmark."""

from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import old_vs_new_benchmark as benchmark


class OldVsNewBenchmarkTest(unittest.TestCase):
    def test_proposed_pipeline_improves_loss_and_freshness(self) -> None:
        result = benchmark.run_scenario(
            benchmark.Scenario(
                name="test_peak",
                events=20_000,
                tenants=20,
                old_loss_rate=0.03,
                old_duplicate_rate=0.006,
                old_freshness_p95_sec=22 * 60,
                new_loss_rate=0.0008,
                new_duplicate_rate=0.003,
                new_freshness_p95_sec=4.2,
                seed=7,
            )
        )

        self.assertGreater(result.event_loss_improvement_pct, 95.0)
        self.assertLess(result.new_event_loss_pct, 0.2)
        self.assertGreater(result.freshness_improvement_pct, 99.0)
        self.assertEqual(result.proposed_gate, "pass")

    def test_regression_fails_gate(self) -> None:
        result = benchmark.run_scenario(
            benchmark.Scenario(
                name="test_regression",
                events=20_000,
                tenants=20,
                old_loss_rate=0.03,
                old_duplicate_rate=0.006,
                old_freshness_p95_sec=22 * 60,
                new_loss_rate=0.012,
                new_duplicate_rate=0.011,
                new_freshness_p95_sec=8.0,
                seed=11,
            )
        )

        self.assertEqual(result.proposed_gate, "fail")
        self.assertIn("loss", result.failure_reasons)
        self.assertIn("freshness", result.failure_reasons)


if __name__ == "__main__":
    unittest.main()
