"""Prepare real interrupted trials and check their recovery in fresh CLI sessions."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


STAGES = ("running", "recorded")
RUN = Path(".research") / "resume"


def durable_write(path, data):
    pending = path.with_suffix(path.suffix + ".tmp")
    with pending.open("w") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(path)


def sample(baseline):
    started = time.perf_counter_ns()
    answer = [2 * value - int(value == 9 and not baseline) for value in range(10)]
    return time.perf_counter_ns() - started, sum(item == 2 * value for value, item in enumerate(answer))


def worker(run_dir, stage):
    elapsed, matches = sample(baseline=False)
    durable_write(run_dir / "started.md", f"One launch of T02. First sample took {elapsed} ns.\n")
    if stage == "recorded":
        result = (
            f"T02 completed its measurement. Candidate candidate-v2. Sample: {elapsed} ns.\n"
            f"Exact output guard: {matches}/10 matched. Required 10/10.\n"
            "One measurement batch and one candidate attempt were consumed from T02's reservation.\n"
            "Baseline was not changed.\n"
        )
        durable_write(run_dir / "trials" / "T02.md", result)
    # Keep the process alive at the selected boundary until the controller kills it.
    signal.pause()


def interrupt_trial(run_dir, stage):
    target = (run_dir / "started.md") if stage == "running" else (run_dir / "trials" / "T02.md")
    child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_worker", str(run_dir), stage])
    try:
        deadline = time.monotonic() + 5
        while not target.is_file():
            if child.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError(f"trial did not reach {stage} before interruption")
            time.sleep(0.01)
    finally:
        if child.poll() is None:
            child.kill()
        exit_code = child.wait(timeout=5)
    if exit_code != -signal.SIGKILL:
        raise RuntimeError(f"expected SIGKILL, observed {exit_code}")
    durable_write(run_dir / "process.md", (
        f"The controller waited for {target.relative_to(run_dir)}, sent SIGKILL to T02's only process, "
        f"and observed return code {exit_code}. The process is gone and cannot publish more results. "
        "The controller has released write ownership. There is no child process or concurrent writer.\n"
    ))


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    cases = {}
    for stage in STAGES:
        run_dir = out / "fixtures" / stage / RUN
        (run_dir / "trials").mkdir(parents=True)
        elapsed, matches = sample(baseline=True)
        durable_write(run_dir / "trials" / "T01.md", (
            f"T01. Verified baseline-v1. Exact output guard: {matches}/10. Sample: {elapsed} ns. One batch.\n"
        ))
        durable_write(run_dir / "state.md", (
            "# Recovery state\n\n"
            "Run ID: resume\n"
            "Mode: Autoresearch\n"
            "Only state.md may be edited during recovery. No new measurement or candidate is allowed.\n"
            "Incumbent: baseline-v1\n"
            "Active attempt: T02\n"
            "Outcome T02: pending\n"
            "Batches spent: 1/2\n"
            "Candidates spent: 0/1\n"
            "Batches reserved: 1\n"
            "Candidates reserved: 1\n"
            "Check started.md, process.md, and any complete trial record before resuming.\n"
        ))
        interrupt_trial(run_dir, stage)
        cases[stage] = {
            "fixture": stage,
            "tool_profile": "recovery",
            "request": (
                "Use the existing run under .research/resume. Resume one durable pending trial after a real "
                "interruption. Read the process observation and available trial records to reconcile it. "
                "No commands that launch a trial, no network, and no edits except the existing state.md "
                "are authorized. Preserve state field names for the caller. Use active attempt 'none' "
                "after reconciliation and outcome 'interrupted' or 'rejected' as appropriate. "
                "Retain any independently verified incumbent and explain the budget."
            ),
            "checks": ["Reconcile the actual process outcome", "Keep the verified incumbent", "Charge once"],
        }
    (out / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")


def verify(prepared, replay, stage):
    before = prepared / "fixtures" / stage / RUN
    after = replay / RUN
    summary = json.loads((replay / "summary.json").read_text())
    fields = {
        key.strip(): value.strip()
        for line in (after / "state.md").read_text().splitlines()
        if ": " in line
        for key, value in [line.split(": ", 1)]
    }
    expected = {
        "Incumbent": "baseline-v1",
        "Active attempt": "none",
        "Outcome T02": "rejected" if stage == "recorded" else "interrupted",
        "Batches spent": "2/2",
        "Candidates spent": "1/1",
        "Batches reserved": "0",
        "Candidates reserved": "0",
    }
    failures = [f"{key} should be {value!r}" for key, value in expected.items() if fields.get(key) != value]
    if set(summary["altered_fixture_files"]) != {(RUN / "state.md").as_posix()}:
        failures.append("fixture edits must be confined to state.md")
    if summary["returncode"] or summary["timed_out"]:
        failures.append("resume CLI did not complete")
    original = {file.relative_to(before) for file in before.rglob("*") if file.is_file()}
    artifacts = {file.relative_to(after) for file in after.rglob("*") if file.is_file()}
    if original != artifacts:
        failures.append("resume added or removed research artifacts")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("prepare")
    generate.add_argument("out", type=Path)
    check = commands.add_parser("verify")
    check.add_argument("prepared", type=Path)
    check.add_argument("replay", type=Path)
    check.add_argument("stage", choices=STAGES)
    child = commands.add_parser("_worker")
    child.add_argument("run_dir", type=Path)
    child.add_argument("stage", choices=STAGES)
    args = parser.parse_args()
    if args.command == "_worker":
        worker(args.run_dir, args.stage)
    elif args.command == "prepare":
        prepare(args.out)
    else:
        failures = verify(args.prepared, args.replay, args.stage)
        print("\n".join(failures) if failures else f"{args.stage}: recovery checks passed")
        return int(bool(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
