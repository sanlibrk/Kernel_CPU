import csv
import io
import json
import math
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "build/scheduler_sim"
BASELINE = ROOT / "build/linux_baseline"
HEADER = "id,class,arrival_ms,burst_ms\n"


class SimulationTests(unittest.TestCase):
    def run_model(self, rows, *options, success=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.csv"
            path.write_text(HEADER + rows)
            result = subprocess.run([str(SIM), *options, str(path)],
                                    capture_output=True, text=True, timeout=10)
        if not success:
            self.assertNotEqual(result.returncode, 0)
            return result
        self.assertEqual(result.returncode, 0, result.stderr)
        return [{k: (v if k == "class" else int(v)) for k, v in row.items()}
                for row in csv.DictReader(io.StringIO(result.stdout))]

    def test_single_task_and_initial_idle(self):
        for policy in ("rr", "interactive"):
            row = self.run_model("1,background,7,9\n", "--policy", policy)[0]
            self.assertEqual((row["start_ms"], row["finish_ms"]), (7, 16))
            self.assertEqual(row["response_ms"], 0)
            self.assertEqual(row["waiting_ms"], 0)

    def test_known_round_robin(self):
        rows = self.run_model("1,background,0,5\n2,background,0,5\n",
                              "--policy", "rr", "--quantum", "2")
        self.assertEqual([r["start_ms"] for r in rows], [0, 2])
        self.assertEqual([r["finish_ms"] for r in rows], [9, 10])

    def test_input_order_does_not_choose_priority(self):
        text = "3,interactive,5,2\n2,background,0,9\n1,background,0,9\n"
        for policy in ("rr", "interactive"):
            a = self.run_model(text, "--policy", policy)
            b = self.run_model("\n".join(reversed(text.strip().splitlines())) + "\n",
                               "--policy", policy)
            self.assertEqual(sorted(a, key=lambda r: r["id"]),
                             sorted(b, key=lambda r: r["id"]))

    def test_interactive_preference_in_controlled_case(self):
        text = "1,background,0,20\n2,background,0,20\n3,interactive,1,1\n"
        rr = self.run_model(text, "--policy", "rr")
        preferred = self.run_model(text, "--policy", "interactive")
        self.assertEqual(rr[2]["start_ms"], 8)
        self.assertEqual(preferred[2]["start_ms"], 4)
        self.assertEqual(max(r["finish_ms"] for r in preferred), 41)

    def test_budget_gives_background_cpu_under_interactive_pressure(self):
        text = "1,background,0,20\n2,interactive,0,80\n3,interactive,0,80\n"
        rows = self.run_model(text, "--aging", "1000000", "--budget", "4")
        self.assertEqual(rows[0]["start_ms"], 4)
        self.assertLess(rows[0]["finish_ms"], 100)

    def test_aging_bypasses_large_interactive_budget(self):
        text = "1,background,0,2\n2,interactive,0,100\n3,interactive,0,100\n"
        rows = self.run_model(text, "--budget", "20", "--aging", "8")
        self.assertEqual(rows[0]["start_ms"], 8)

    def test_no_artificial_idle_when_only_interactive_tasks(self):
        rows = self.run_model("1,interactive,0,31\n2,interactive,0,29\n",
                              "--budget", "1")
        self.assertEqual(max(r["finish_ms"] for r in rows), 60)

    def test_background_only_matches_rr(self):
        text = "1,background,0,19\n2,background,1,7\n3,background,0,25\n"
        self.assertEqual(self.run_model(text, "--policy", "rr"),
                         self.run_model(text, "--policy", "interactive"))

    def test_randomized_accounting_and_all_tasks_complete(self):
        rng = random.Random(210504018)
        for case in range(20):
            workload = [(i + 1, rng.choice(("background", "interactive")),
                         rng.randrange(15), rng.randrange(1, 30)) for i in range(12)]
            workload[0] = (1, "background", 0, 80)  # no idle gaps in this fixture
            text = "".join(f"{i},{c},{a},{b}\n" for i, c, a, b in workload)
            for policy in ("rr", "interactive"):
                with self.subTest(case=case, policy=policy):
                    rows = self.run_model(text, "--policy", policy)
                    self.assertEqual(len(rows), len(workload))
                    self.assertEqual(max(r["finish_ms"] for r in rows),
                                     sum(t[3] for t in workload))
                    for row in rows:
                        self.assertGreaterEqual(row["start_ms"], row["arrival_ms"])
                        self.assertGreaterEqual(row["waiting_ms"], 0)
                        self.assertEqual(row["waiting_ms"] + row["burst_ms"],
                                         row["turnaround_ms"])
                        self.assertLessEqual(row["response_ms"], row["waiting_ms"])

    def test_invalid_workloads_rejected(self):
        bad = ("", "1,background,0,0\n", "1,interactive,-1,2\n",
               "1,unknown,0,1\n", "1,background,0,1\n1,background,2,1\n",
               "1,background,0,2,extra\n", "1,background,0,no\n",
               "1,background,0,1000001\n", "1,background,0,2\ninvalid\n")
        for text in bad:
            with self.subTest(text=text):
                self.run_model(text, success=False)

    def test_invalid_options_rejected(self):
        for options in (("--quantum", "0"), ("--budget", "21"),
                        ("--policy", "linux"), ("--aging", "-1")):
            self.run_model("1,background,0,1\n", *options, success=False)


class LinuxBaselineTests(unittest.TestCase):
    def test_real_measurements_with_and_without_workers(self):
        for workers in (0, 2):
            with self.subTest(workers=workers):
                result = subprocess.run([str(BASELINE), "--workers", str(workers),
                                         "--samples", "4", "--period-ms", "2",
                                         "--burst-us", "100", "--worker-ms", "20"],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data["sample_count"], 4)
                self.assertEqual(data["scheduler"], "SCHED_OTHER")
                self.assertEqual(len(data["background"]), workers)
                self.assertEqual(len(data["samples"]), 4)
                self.assertLessEqual(data["wake_p50_ms"], data["wake_p95_ms"])
                self.assertLessEqual(data["wake_p95_ms"], data["wake_max_ms"])
                for sample in data["samples"]:
                    for value in sample.values():
                        self.assertTrue(math.isfinite(value))
                    self.assertGreaterEqual(sample["wake_lateness_ms"], 0)
                    self.assertGreaterEqual(sample["completion_latency_ms"],
                                            sample["wake_lateness_ms"])
                    self.assertGreaterEqual(sample["cpu_ms"], 0.1)
                for worker in data["background"]:
                    self.assertGreaterEqual(worker["cpu_ms"], 20)
                    # Clock sampling has a small cost outside the timed CPU loop.
                    self.assertGreaterEqual(worker["wall_ms"] + 0.1, worker["cpu_ms"])

    def test_invalid_measurement_options_rejected(self):
        for args in (("--workers", "9"), ("--samples", "0"),
                     ("--period-ms", "-1"), ("--unknown", "2")):
            result = subprocess.run([str(BASELINE), *args], capture_output=True,
                                    text=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
