#!/usr/bin/env python3
"""Host-side launcher for two separate Podman roles. Uses only the Python standard library."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent
IMAGE = "localhost/grading-agent:hw2"
DEFAULT_URL = "http://host.containers.internal:11434"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def send(pipe, obj):
    pipe.write(json.dumps(obj, ensure_ascii=False) + "\n")
    pipe.flush()


def save(path, report):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_cases(path):
    cases = read_json(path)
    indexed = {c["case_id"]: c for c in cases}
    if len(indexed) != len(cases) or any(not isinstance(c[k], str) for c in cases for k in ("case_id", "stdin", "expected_stdout")):
        raise ValueError(f"Invalid cases: {path.name}")
    return indexed


def normalized(value):
    return value.replace("\r\n", "\n").replace("\r", "\n").removesuffix("\n")


def execute(source, case):
    command = ["podman", "run", "--rm", "-i", "--pull=never", "--network=none", "--read-only",
               "--tmpfs=/tmp:rw,nosuid,nodev,noexec,size=8m,mode=1777", "--pids-limit=32",
               "--memory=128m", "--cpus=1", "--cap-drop=ALL", "--cap-add=SETUID",
               "--cap-add=SETGID", "--cap-add=KILL", "--security-opt=no-new-privileges",
               "--timeout=20", IMAGE, "python", "-I", "-B", "/opt/grader/worker.py"]
    proc = subprocess.run(command, input=json.dumps({"stdin": case["stdin"], "source": source}),
                          capture_output=True, text=True, timeout=45)
    if proc.returncode:
        raise RuntimeError(f"Podman worker failed ({proc.returncode}): {proc.stderr.strip()[-1200:]}")
    row = json.loads(proc.stdout)
    if row["status"] == "completed":
        row["status"] = "pass" if normalized(row["actual_stdout"]) == normalized(case["expected_stdout"]) else "wrong_output"
    return dict(case, **row)


class TestTools:
    def __init__(self, source, official, probes):
        self.source = source
        self.official = official
        self.probes = probes
        self.results = {}

    def call(self, name, case_id):
        if name == "run_official" and not self.results and case_id is None:
            for key, case in self.official.items():
                self.results[key] = execute(self.source, case)
            return list(self.results.values())
        if name == "inspect_case" and case_id in self.official and case_id in self.results:
            return self.results[case_id]
        if name == "run_probe" and case_id in self.probes and case_id not in self.results:
            row = execute(self.source, self.probes[case_id])
            self.results[case_id] = row
            return row
        raise ValueError(f"Tool request unavailable: {name}, {case_id}")


def run_agent(args, report, output, job, tools):
    # No file mounts, Podman socket or teacher answer key enter the application container.
    command = ["podman", "run", "--rm", "-i", "--pull=never", "--read-only",
               "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
               "--memory=256m", "--pids-limit=32", "--env", "GRADER_OLLAMA_URL=" + args.ollama_url, IMAGE]
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          text=True, encoding="utf-8") as agent:
        try:
            send(agent.stdin, job)
            result = None
            for line in agent.stdout:
                item = json.loads(line)
                if item["type"] == "event":
                    report["trace"].append(item)
                elif item["type"] == "tool":
                    report["trace"].append({"type": "tool_call", "name": item["name"], "case_id": item["case_id"]})
                    try:
                        observed = tools.call(item["name"], item["case_id"])
                        reply = {"observation": observed}
                    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError, KeyError) as exc:
                        reply = {"error": str(exc)}
                    report["trace"].append({"type": "observation", **reply})
                    save(output, report)
                    send(agent.stdin, reply)
                elif item["type"] == "result":
                    result = item["result"]
                    break
            agent.stdin.close()
            if agent.wait() or result is None:
                raise RuntimeError("Application container exited without a usable result. Check Podman and the project image.")
            return result
        finally:
            if not agent.stdin.closed:
                agent.stdin.close()


def main():
    parser = argparse.ArgumentParser(description="Run the HW2 programming assignment grading agent.")
    parser.add_argument("--lang", choices=["en", "zh-Hant"], default="en")
    parser.add_argument("--task", choices=["01_scores", "02_parking", "03_words"], default="01_scores")
    parser.add_argument("--sample", default="S03", help="Packaged sample ID, e.g. S03")
    parser.add_argument("--file", type=Path, help="Grade a different single UTF-8 .py file instead.")
    parser.add_argument("--max-checks", type=int, default=2, choices=range(5))
    parser.add_argument("--model", default=os.getenv("GRADER_MODEL", "llama3.2:3b"))
    parser.add_argument("--ollama-url", default=os.getenv("GRADER_OLLAMA_URL", DEFAULT_URL))
    args = parser.parse_args()
    base = ROOT / "grading_lab" / args.lang / args.task
    if args.file is None and args.sample not in {f"S{i:02}" for i in range(1, 16)}:
        parser.error("Sample must be S01–S15, or supply --file.")
    path = args.file or base / "submissions" / (args.sample + ".py")
    try:
        if path.suffix != ".py" or path.stat().st_size > 16384:
            raise ValueError("Expected a .py submission of at most 16 KiB.")
        source = path.read_text(encoding="utf-8")
        official = load_cases(base / "official_tests.json")
        probes = load_cases(base / "diagnostic_tests.json")
        rubric = read_json(base / "rubric.json")
        if len(official) != 10 or [part["points"] for part in rubric] != [60,25,10,5] or official.keys() & probes.keys():
            raise ValueError("This milestone supports the bundled 10-case 60/25/10/5 rubric.")
        job = dict(model=args.model, language=args.lang, assignment=(base / "assignment.md").read_text(encoding="utf-8"),
                   rubric=rubric, source=source, probe_ids=list(probes), max_checks=args.max_checks)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
    output = ROOT / "runs" / (run_id + ".json")
    output.parent.mkdir(exist_ok=True)
    report = dict(run_id=run_id, started=now.isoformat(), task=args.task, language=args.lang,
                  submission=path.name, sha256=hashlib.sha256(source.encode()).hexdigest(),
                  model=args.model, ollama_url=args.ollama_url, max_checks=args.max_checks,
                  trace=[{"type":"user_input", "task":args.task, "submission":path.name, "language":args.lang}],
                  result={"status":"running"})
    tools = TestTools(source, official, probes)
    save(output, report)
    try:
        result = run_agent(args, report, output, job, tools)
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as exc:
        result = {"status": "pending", "reason": str(exc)}
    report["result"] = result
    report["finished"] = datetime.now(timezone.utc).isoformat()
    report["test_results"] = list(tools.results.values())
    save(output, report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Trace:", output.relative_to(ROOT))
    return 2 if result["status"] == "pending" else 0


if __name__ == "__main__":
    sys.exit(main())
