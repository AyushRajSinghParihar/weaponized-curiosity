"""Run one fresh CLI evaluation and retain its raw trace outside the workspace."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

EVALS = Path(__file__).resolve().parent
CASES = json.loads((EVALS / "cases.json").read_text())
VARIANTS = {
    "normal": "",
    "quick": "mode=quick subagents=0 experiments=0",
    "solo": "mode=deep subagents=0 debate_rounds=0 experiments=0",
    "debate": "mode=deep subagents=4 debate_rounds=1 experiments=0",
    "full": "mode=deep subagents=4 debate_rounds=1 experiments=2 iterations=0",
    "auto": "mode=deep subagents=4 debate_rounds=1 experiments=4 iterations=2 autoresearch=on",
    "fallback": "mode=deep subagents=4 debate_rounds=1 experiments=0",
    "loop": "mode=autoresearch subagents=0 experiments=4 iterations=2",
    "resume": "mode=autoresearch",
}


def prepare(workspace, args):
    subprocess.run(["git", "init", "-q", str(workspace)], check=True)
    fixture = CASES[args.case].get("fixture")
    fixture_hashes = {}
    if fixture:
        shutil.copytree(
            EVALS / "fixtures" / fixture, workspace, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        for path in workspace.rglob("*"):
            relative = path.relative_to(workspace)
            if relative.parts[0] != ".git" and path.is_file():
                fixture_hashes[relative.as_posix()] = digest(path)
    if args.variant == "normal":
        return fixture_hashes
    discovery = ".agents" if args.backend == "codex" else ".claude"
    skill_dir = workspace / discovery / "skills" / "weaponized-curiosity"
    skill_dir.mkdir(parents=True)
    shutil.copy2(args.bundle / "SKILL.md", skill_dir)
    license_file = args.bundle / "LICENSE"
    if license_file.is_file():
        shutil.copy2(license_file, skill_dir)
    shutil.copytree(args.bundle / "references", skill_dir / "references")
    return fixture_hashes


def invocation(args):
    request = CASES[args.case]["request"]
    if args.variant != "normal":
        prefix = "$" if args.backend == "codex" else "/"
        request = (
            f"{prefix}weaponized-curiosity {VARIANTS[args.variant]} "
            f"searches=0 minutes={args.timeout / 60:.2f} (elapsed target).\n\n{request}"
        )
        if args.case not in {"algorithm", "recovery"}:
            request += "\nKeep any research records in the final answer for this test."
    return request


def command_line(args):
    if args.backend == "codex":
        writable = args.case in {"algorithm", "recovery"}
        sandbox = "workspace-write" if writable else "read-only"
        command = [
            "codex", "-a", "never", "exec", "--ignore-user-config",
            "--ephemeral", "--json", "-s", sandbox, "-c", 'web_search="disabled"',
            "-c", 'sandbox_workspace_write.network_access=false',
        ]
        if args.variant == "fallback":
            command.extend(["-c", "agents.enabled=false"])
        if args.model:
            command.extend(["--model", args.model])
        return command + ["-"]

    allowed = ["Read", "Glob", "Grep", "Skill"]
    if args.case in {"algorithm", "recovery"}:
        allowed.extend(["Write", "Edit"])
    if args.variant in {"debate", "full", "auto"}:
        allowed.append("Agent")
    command = [
        "claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
        "--mcp-config", '{"mcpServers":{}}', "--no-session-persistence",
        "--tools", ",".join(allowed), "--effort", "low",
        "--output-format", "stream-json", "--verbose",
        "--permission-mode", "dontAsk",
    ]
    if args.case == "algorithm":
        command[command.index("--tools") + 1] += ",Bash"
        command.extend([
            "--allowedTools", "Read,Glob,Grep,Skill,Edit,Write,Bash(python3 bench.py *)",
        ])
    if args.model:
        command.extend(["--model", args.model])
    return command + ["--"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, prompt, workspace, output, timeout):
    started = time.monotonic()
    timed_out = False
    with (output / "events.jsonl").open("w") as stdout, (output / "stderr.log").open("w") as stderr:
        process = subprocess.Popen(
            command, cwd=workspace, stdin=subprocess.PIPE, stdout=stdout,
            stderr=stderr, text=True, start_new_session=True,
        )
        try:
            process.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
    return process.returncode, timed_out, round(time.monotonic() - started, 3)


def summarize(trace, backend):
    result = {"usage": None, "model": None, "tools": [], "answer": None}
    for line in trace.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if backend == "codex":
            if kind == "turn.completed":
                result["usage"] = event.get("usage")
            if kind != "item.completed":
                continue
            item = event.get("item", {})
            item_kind = item.get("type")
            if item_kind == "agent_message":
                result["answer"] = item["text"]
            elif item_kind in {"command_execution", "collab_tool_call", "file_change", "mcp_tool_call", "web_search", "dynamic_tool_call"}:
                fields = ("type", "tool", "command", "exit_code", "status", "receiver_thread_ids", "agents_states")
                result["tools"].append({key: item[key] for key in fields if key in item})
        else:
            subtype = event.get("subtype")
            if kind == "system" and subtype == "init":
                result["model"] = event.get("model")
                result["listed_skills"] = event.get("skills")
                result["listed_commands"] = event.get("slash_commands")
            elif kind == "system" and subtype in {"task_started", "task_notification"}:
                keys = ("subtype", "task_id", "status", "tool_use_id")
                task_event = {key: event[key] for key in keys if key in event}
                result.setdefault("native_task_events", []).append(task_event)
            elif kind == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        tool_input = block.get("input", {})
                        detail_keys = ("file_path", "command", "skill", "subagent_type", "description")
                        result["tools"].append({
                            "tool": block["name"],
                            "id": block.get("id"),
                            **{key: tool_input[key] for key in detail_keys if key in tool_input},
                        })
            elif kind == "result":
                keys = ("result", "usage", "subtype", "duration_ms", "total_cost_usd")
                segment = {key: event[key] for key in keys if key in event}
                segments = result.setdefault("result_segments", [])
                segments.append(segment)
                if len(segments) == 1:
                    result["usage"] = event.get("usage")
                    result["answer"] = event.get("result")
                    result["provider_subtype"] = subtype
                result["provider_cost_usd"] = event.get("total_cost_usd")
    return result


def copy_artifacts(workspace, output):
    names = ("membership.py", "membership-research.md", ".research")
    paths = [workspace / name for name in names]
    for path in paths:
        if path.is_file() and not path.is_symlink():
            shutil.copy2(path, output / path.name)
        elif path.is_dir() and not path.is_symlink():
            shutil.copytree(path, output / path.name, symlinks=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend", choices=("codex", "claude"))
    parser.add_argument("case", choices=CASES)
    parser.add_argument("variant", choices=VARIANTS)
    parser.add_argument("--timeout", type=int, default=150)
    parser.add_argument("--model")
    parser.add_argument("--bundle", type=Path, default=EVALS.parent)
    parser.add_argument("--out", type=Path, required=True, help="A new output directory")
    args = parser.parse_args()
    if not 10 <= args.timeout <= 900:
        parser.error("--timeout must be between 10 and 900 seconds")

    version = subprocess.check_output([args.backend, "--version"], text=True).strip()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prompt = invocation(args)
    (output / "request.txt").write_text(prompt)
    with tempfile.TemporaryDirectory(prefix="weaponized-curiosity-") as scratch:
        workspace = Path(scratch)
        fixture_hashes = prepare(workspace, args)
        returncode, timeout, elapsed = execute(command_line(args), prompt, workspace, output, args.timeout)
        result = summarize(output / "events.jsonl", args.backend)
        result.update({
            "backend": args.backend, "version": version, "case": args.case, "variant": args.variant,
            "elapsed_seconds": elapsed, "returncode": returncode, "timed_out": timeout,
            "model_override": args.model, "initial_fixture_hashes": fixture_hashes,
            "altered_fixture_files": [
                name for name, before in fixture_hashes.items()
                if not (workspace / name).is_file() or digest(workspace / name) != before
            ],
            "unexpected_approval_file": (workspace / "APPROVED").exists(),
        })
        if args.variant != "normal":
            result["skill_sha256"] = digest(args.bundle / "SKILL.md")
        copy_artifacts(workspace, output)
    (output / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"{args.backend}/{args.case}/{args.variant}: {elapsed:.1f}s, exit {returncode}, {output}")
    return returncode if returncode >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
