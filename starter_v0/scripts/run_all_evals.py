import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

suites = [
    ("Base Suite", "base", ROOT / "data" / "eval_base.json"),
    ("Extension Suite", "extension", ROOT / "data" / "eval_helpdesk_extension.json"),
    ("Adversarial Suite", "adversarial", ROOT / "data" / "eval_adversarial.json"),
    ("Group Suite (10 cases)", "group", ROOT / "data" / "eval_group.json"),
]

print("=" * 70)
print("           NORTHSTAR LABS IT HELPDESK AGENT - FINAL BENCHMARK")
print("=" * 70)

for title, suite_label, eval_path in suites:
    print(f"\n>>> Running: {title} ({eval_path.name}) ...")
    cmd = [
        PYTHON,
        str(ROOT / "run_eval.py"),
        "--provider", "openai",
        "--version", "v5_final",
        "--suite", suite_label,
        "--eval-cases", str(eval_path),
    ]
    res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    lines = res.stdout.strip().splitlines()
    summary_lines = [line for line in lines if any(k in line for k in ("total_cases:", "passed_cases:", "case_accuracy:", "tool_routing_accuracy:", "argument_accuracy:", "multiturn_accuracy:", "failure_counts:", "observed_mismatch_counts:"))]
    for sl in summary_lines:
        print("   " + sl)

print("\n" + "=" * 70)
print("                     FINAL BENCHMARK COMPLETE")
print("=" * 70)
