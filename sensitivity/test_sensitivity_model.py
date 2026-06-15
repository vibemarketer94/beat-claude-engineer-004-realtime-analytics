#!/usr/bin/env python3
"""Regression tests for the sensitivity sweep model."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("sensitivity_model.py")
spec = importlib.util.spec_from_file_location("sensitivity_model", MODULE_PATH)
sensitivity_model = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["sensitivity_model"] = sensitivity_model
spec.loader.exec_module(sensitivity_model)


class SensitivityModelTests(unittest.TestCase):
    def test_sensitivity_sweep_names_cliff_edges(self) -> None:
        rows = sensitivity_model.run_sweep()
        names = {row.scenario for row in rows}

        self.assertIn("brief_peak", names)
        self.assertIn("large_payload_10x", names)
        self.assertIn("tenant_skew_35pct", names)
        self.assertIn("late_events_15pct", names)
        self.assertIn("export_write_amp_6x", names)
        self.assertIn("cost_ceiling_pressure", names)

    def test_sensitivity_flags_scale_and_budget_cliffs(self) -> None:
        rows = {row.scenario: row for row in sensitivity_model.run_sweep()}

        self.assertEqual(rows["brief_peak"].gate, "pass")
        self.assertEqual(rows["tenant_skew_35pct"].gate, "manual_review")
        self.assertGreater(rows["large_payload_10x"].stream_mbps, rows["brief_peak"].stream_mbps)
        self.assertGreater(rows["cost_ceiling_pressure"].monthly_cost, sensitivity_model.MONTHLY_BUDGET)
        self.assertEqual(rows["cost_ceiling_pressure"].gate, "fail")


if __name__ == "__main__":
    unittest.main()
