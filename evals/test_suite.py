"""Offline checks for the bundle, fixture, and CLI evaluation wrapper."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

import run

ROOT = Path(__file__).resolve().parents[1]


class BundleTests(unittest.TestCase):
    def test_metadata_and_progressive_links(self):
        skill = (ROOT / "SKILL.md").read_text()
        delimiter, metadata, body = skill.split("---\n", 2)
        self.assertEqual(delimiter, "")
        fields = dict(line.split(": ", 1) for line in metadata.strip().splitlines())
        self.assertEqual(fields["name"], "weaponized-curiosity")
        self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertTrue(0 < len(fields["description"]) <= 1024)
        self.assertLessEqual(len(body.splitlines()), 100)
        referenced = {Path(path).name for path in re.findall(r"\]\((references/[^)#]+)", body)}
        available = {path.name for path in (ROOT / "references").glob("*.md")}
        self.assertEqual(referenced, available)

    def test_native_bundle_installation_and_control(self):
        for host, folder in [("codex", ".agents"), ("claude", ".claude")]:
            for variant in ["quick", "normal"]:
                with self.subTest(host=host, variant=variant), tempfile.TemporaryDirectory() as scratch:
                    workspace = Path(scratch)
                    args = argparse.Namespace(backend=host, case="algorithm", variant=variant, bundle=ROOT)
                    initial = run.prepare(workspace, args)
                    skill = workspace / folder / "skills" / "weaponized-curiosity"
                    self.assertEqual((skill / "SKILL.md").exists(), variant != "normal")
                    self.assertEqual(set(initial), {"membership.py", "bench.py"})
                    self.assertFalse((workspace / "cases.json").exists())
                    if variant != "normal":
                        self.assertEqual(
                            sorted(p.name for p in (skill / "references").iterdir()),
                            sorted(p.name for p in (ROOT / "references").iterdir()),
                        )


class RunnerTests(unittest.TestCase):
    def test_timeout_preserves_trace_and_does_not_hang(self):
        with tempfile.TemporaryDirectory() as scratch:
            workspace = Path(scratch)
            command = [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(20)"]
            status, timed_out, elapsed = run.execute(command, "", workspace, workspace, 0.5)
            self.assertTrue(timed_out)
            self.assertNotEqual(status, 0)
            self.assertLess(elapsed, 5)
            self.assertIn("started", (workspace / "events.jsonl").read_text())

    def test_summary_extracts_native_events_without_inventing_them(self):
        fixtures = {
            "codex": [
                {"type": "item.completed", "item": {"type": "collab_tool_call", "tool": "spawn_agent",
                    "status": "completed", "receiver_thread_ids": ["example"]}},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "Example verdict"}},
                {"type": "turn.completed", "usage": {"input_tokens": 41}},
            ],
            "claude": [
                {"type": "system", "subtype": "init", "skills": ["weaponized-curiosity"], "model": "example"},
                {"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Task", "input": {"description": "Read independently"}},
                ]}},
                {"type": "system", "subtype": "task_notification", "status": "completed"},
                {"type": "result", "result": "Example verdict", "usage": {"input_tokens": 41}},
                {"type": "result", "result": "Late reviewer note", "usage": {"input_tokens": 9}},
            ],
        }
        with tempfile.TemporaryDirectory() as scratch:
            trace = Path(scratch) / "events.jsonl"
            for host, events in fixtures.items():
                with self.subTest(host=host):
                    trace.write_text("\n".join(map(json.dumps, events)))
                    result = run.summarize(trace, host)
                    self.assertEqual(result["answer"], "Example verdict")
                    self.assertEqual(result["usage"]["input_tokens"], 41)
                    self.assertEqual(len(result["tools"]), 1)
                    expected_tool = "spawn_agent" if host == "codex" else "Task"
                    self.assertEqual(result["tools"][0]["tool"], expected_tool)
                    if host == "claude":
                        self.assertEqual(result["result_segments"][1]["result"], "Late reviewer note")
                        self.assertEqual(result["native_task_events"][0]["status"], "completed")


class FixtureTests(unittest.TestCase):
    def test_algorithm_contract(self):
        source = ROOT / "evals" / "fixtures" / "algorithm" / "membership.py"
        spec = importlib.util.spec_from_file_location("membership", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        values = [1, 1, -10**30]
        queries = [0, 1, -10**30, 1, 10**30]
        self.assertEqual(module.batch_membership(values, queries), [False, True, True, True, False])
        self.assertEqual(values, [1, 1, -10**30])
        self.assertEqual(queries, [0, 1, -10**30, 1, 10**30])
        self.assertEqual(module.batch_membership([], []), [])

    def test_profile_fixture_cannot_meet_target_through_parser_only(self):
        source = ROOT / "evals" / "fixtures" / "performance" / "profile.csv"
        with source.open() as stream:
            rows = list(csv.DictReader(stream))
        for state, expected in [("warm", (129, 122)), ("cold", (212, 206))]:
            cohort = [row for row in rows if row["state"] == state]
            self.assertEqual(len(cohort), 30)
            total = sorted(int(row["total_ms"]) for row in cohort)
            no_parse = sorted(int(row["total_ms"]) - int(row["parse_ms"]) for row in cohort)
            self.assertEqual((total[28], no_parse[28]), expected)
            self.assertLess((total[28] - no_parse[28]) / total[28], 0.10)


if __name__ == "__main__":
    unittest.main()
