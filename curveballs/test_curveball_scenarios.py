#!/usr/bin/env python3
"""Regression tests for reviewer curveball scenarios."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("curveball_scenarios.py")
spec = importlib.util.spec_from_file_location("curveball_scenarios", MODULE_PATH)
curveball_scenarios = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["curveball_scenarios"] = curveball_scenarios
spec.loader.exec_module(curveball_scenarios)


class CurveballScenarioTests(unittest.TestCase):
    def test_curveballs_include_private_reviewer_failure_modes(self) -> None:
        results = curveball_scenarios.evaluate_scenarios()
        names = {row["scenario"] for row in results}

        self.assertIn("tenant_hotspot", names)
        self.assertIn("missing_event_id", names)
        self.assertIn("gdpr_delete_during_replay", names)
        self.assertIn("warehouse_export_failure", names)
        self.assertIn("kinesis_backpressure", names)
        self.assertIn("sdk_clock_skew", names)

    def test_curveball_gates_choose_safe_operating_action(self) -> None:
        rows = {row["scenario"]: row for row in curveball_scenarios.evaluate_scenarios()}

        self.assertEqual(rows["tenant_hotspot"]["action"], "isolate tenant and keep old read path")
        self.assertEqual(rows["missing_event_id"]["action"], "accept with server id and warning")
        self.assertEqual(rows["gdpr_delete_during_replay"]["action"], "block cutover until tombstones reconcile")
        self.assertEqual(rows["warehouse_export_failure"]["gate"], "fail")
        self.assertEqual(rows["kinesis_backpressure"]["loss_budget_ok"], "yes")
        self.assertEqual(rows["sdk_clock_skew"]["gate"], "pass_with_warning")


if __name__ == "__main__":
    unittest.main()
