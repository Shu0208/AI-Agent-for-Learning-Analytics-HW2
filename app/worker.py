"""Run one supplied program and one input in a disposable, offline container."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile

OUTPUT_LIMIT = 16384


def limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT, OUTPUT_LIMIT))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    request = json.load(sys.stdin)
    with tempfile.TemporaryDirectory(dir="/tmp") as directory:
        path = Path(directory, "submission.py")
        path.write_text(request["source"], encoding="utf-8")
        path.chmod(0o444)
        os.chmod(directory, 0o755)
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            with subprocess.Popen(
                [sys.executable, "-I", "-B", str(path)], cwd=directory,
                stdin=subprocess.PIPE, stdout=out, stderr=err,
                user=65534, group=65534, extra_groups=[], start_new_session=True,
                preexec_fn=limits, env={"LANG": "C.UTF-8", "PATH": "/usr/local/bin:/usr/bin:/bin"},
            ) as child:
                try:
                    child.communicate(request["stdin"].encode(), timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                    return {"status": "timeout", "detail": "Student exceeded 2 seconds."}
            out.seek(0)
            err.seek(0)
            output, error = out.read(), err.read()
            if max(len(output), len(error)) >= OUTPUT_LIMIT:
                return {"status": "output_limit", "detail": "16 KiB output limit reached."}
            error = error.decode(errors="replace").replace(str(path), "submission.py")
            if child.returncode:
                kind = "syntax_error" if error.rstrip().splitlines() and error.rstrip().splitlines()[-1].startswith(("SyntaxError:", "IndentationError:", "TabError:")) else "runtime_error"
                return {"status": kind, "detail": error[-1500:], "exit_code": child.returncode}
            return {"status": "completed", "actual_stdout": output.decode(errors="replace")}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False))
