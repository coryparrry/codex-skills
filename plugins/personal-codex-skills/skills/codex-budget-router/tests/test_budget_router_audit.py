import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import budget_router_audit as audit


def row(**values):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    columns = ", ".join(f":{key} as {key}" for key in values)
    return conn.execute(f"select {columns}", values).fetchone()


class BudgetRouterAuditTests(unittest.TestCase):
    def test_child_share_handles_zero_total(self):
        self.assertEqual(audit.child_share(0, 0), 0.0)

    def test_verdict_requires_workers(self):
        result = audit.verdict_for(
            row(
                child_count=0,
                spark_count=0,
                child_mix="",
                root_tokens=100,
                child_tokens=0,
            )
        )
        self.assertEqual(result, "FAIL no workers")

    def test_verdict_flags_missing_spark_for_implementation_worker(self):
        result = audit.verdict_for(
            row(
                child_count=1,
                spark_count=0,
                child_mix="codex_worker:gpt-5.3-codex:100",
                root_tokens=100,
                child_tokens=100,
            )
        )
        self.assertEqual(result, "WEAK no Spark")

    def test_verdict_reports_material_displacement(self):
        result = audit.verdict_for(
            row(
                child_count=2,
                spark_count=1,
                child_mix="spark_worker:gpt-5.3-codex-spark:100",
                root_tokens=100,
                child_tokens=100,
            )
        )
        self.assertEqual(result, "GOOD material displacement")

    def test_totals_aggregate_rows(self):
        rows = [
            row(
                root_tokens=100,
                child_tokens=50,
                child_count=1,
                spark_count=1,
                spark_tokens=25,
            ),
            row(
                root_tokens=10,
                child_tokens=5,
                child_count=2,
                spark_count=0,
                spark_tokens=0,
            ),
        ]
        self.assertEqual(
            audit.totals(rows),
            {
                "root": 110,
                "child": 55,
                "workers": 3,
                "spark_workers": 1,
                "spark_tokens": 25,
                "threads": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
