#!/usr/bin/env python3
"""Collect fresh model results and real Linux baselines; do not create a PDF."""
import csv
from datetime import datetime
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def source_hashes():
    files = [ROOT / "Makefile", ROOT / "README.md", ROOT / ".gitignore",
             ROOT / "Kernel_CPU.code-workspace"]
    for name in ("src", "scripts", "tests", "workloads", "docs"):
        files.extend(p for p in (ROOT / name).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}


def summarize(rows):
    result = {"task_count": len(rows), "makespan_ms": max(r["finish_ms"] for r in rows)}
    for kind in ("interactive", "background"):
        group = [r for r in rows if r["class"] == kind]
        result[kind] = {"count": len(group)}
        if group:
            values = sorted(r["response_ms"] for r in group)
            result[kind].update(response_mean_ms=statistics.mean(values),
                response_p95_ms=values[math.ceil(len(values) * .95) - 1],
                waiting_mean_ms=statistics.mean(r["waiting_ms"] for r in group),
                turnaround_mean_ms=statistics.mean(r["turnaround_ms"] for r in group))
    return result


def run():
    now = datetime.now(ZoneInfo("Europe/Istanbul"))
    directory = ROOT / "results" / now.strftime("week2-%Y%m%d-%H%M%S-%f")
    directory.mkdir(parents=True, exist_ok=False)
    subprocess.run(["make", "all"], cwd=ROOT, check=True)
    tests = subprocess.run(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
    log = tests.stdout + tests.stderr
    (directory / "tests.txt").write_text(log)
    if tests.returncode:
        raise RuntimeError(f"Tests failed; see {directory / 'tests.txt'}")
    match = re.search(r"Ran (\d+) tests?", log)
    if not match or int(match.group(1)) == 0 or "skipped=" in log:
        raise RuntimeError("Expected a completed suite with no skipped tests")
    info = {"created_at": now.isoformat(),
        "environment": {"kernel": platform.release(), "machine": platform.machine(),
            "os_release": platform.freedesktop_os_release().get("PRETTY_NAME"),
            "allowed_cpus": sorted(os.sched_getaffinity(0)),
            "sched_ext_visible": Path("/sys/kernel/sched_ext/state").exists(),
            "btf_visible": Path("/sys/kernel/btf/vmlinux").exists()},
        "tests": {"passed": int(match.group(1)), "failed": 0, "skipped": 0},
        "policy_parameters": {"quantum_ms": 4, "window_ms": 20,
            "interactive_budget_ms": 8, "aging_ms": 20},
        "model": {}, "linux_baseline": []}
    for name in ("cpu.max", "cpu.stat", "memory.max"):
        p = Path("/sys/fs/cgroup") / name
        if p.exists():
            info["environment"]["cgroup_" + name] = p.read_text().strip()
    for path in sorted((ROOT / "workloads").glob("*.csv")):
        info["model"][path.stem] = {}
        for policy in ("rr", "interactive"):
            command = [str(ROOT / "build/scheduler_sim"), "--policy", policy,
                "--quantum", "4", "--window", "20", "--budget", "8", "--aging", "20", str(path)]
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=20)
            filename = f"model-{path.stem}-{policy}.csv"
            (directory / filename).write_text(result.stdout)
            rows = [{k: (v if k == "class" else int(v)) for k, v in row.items()}
                    for row in csv.DictReader(io.StringIO(result.stdout))]
            info["model"][path.stem][policy] = {**summarize(rows), "file": filename}
    for repetition in range(1, 4):
        for workers in (0, 2):
            command = [str(ROOT / "build/linux_baseline"), "--workers", str(workers),
                "--samples", "40", "--period-ms", "20", "--burst-us", "500", "--worker-ms", "800"]
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            data = json.loads(result.stdout)
            if data["sample_count"] != 40 or len(data["samples"]) != 40:
                raise RuntimeError("Incomplete Linux measurement")
            if len(data["background"]) != workers:
                raise RuntimeError("Missing worker completion records")
            filename = f"linux-workers{workers}-run{repetition}.json"
            (directory / filename).write_text(json.dumps(data, indent=2) + "\n")
            info["linux_baseline"].append({"file": filename, "repetition": repetition,
                **{k: v for k, v in data.items() if k not in ("samples", "background")},
                "background_wall_ms": [w["wall_ms"] for w in data["background"]]})
    info["source_sha256"] = source_hashes()
    (directory / "summary.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n")
    latest = ROOT / "results/latest.json"
    temp = latest.with_suffix(".tmp")
    temp.write_text(json.dumps({"directory": str(directory.relative_to(ROOT))}) + "\n")
    temp.replace(latest)
    print(f"Results: {directory}")
    print(f"Tests: {info['tests']['passed']} passed; 6 model runs; 6 Linux runs, 240 samples.")


if __name__ == "__main__":
    run()
