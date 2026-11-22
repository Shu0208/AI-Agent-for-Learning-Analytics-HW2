"""Reconcile saved Podman runs with the independent teacher key, without Ollama."""
import argparse
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent


def verify(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    key_path = ROOT / "grading_lab" / "teacher_only" / data["language"] / (data["task"] + ".json")
    key = next(row for row in json.loads(key_path.read_text(encoding="utf-8"))
               if row["submission"] + ".py" == data["submission"])
    expected = {row["case_id"]: row for row in key["results"]}
    observed = {row["case_id"]: row for row in data["test_results"]}
    official_ids = {i for i in expected if i.startswith("T")}
    assert official_ids <= observed.keys(), "Missing official test results"
    for identifier, row in observed.items():
        oracle = expected[identifier]
        assert row["status"] == oracle["status"], identifier
        if "actual_stdout" in oracle:
            assert row["actual_stdout"] == oracle["actual_stdout"], identifier
    result = data["result"]
    assert result["official_passes"] == key["official_passes"]
    assert result["functional_points"] == key["functional_points"]
    if result["status"] == "proposed":
        assert result["total"] == result["functional_points"] + sum(result[n]["points"] for n in ("algorithm","specification","readability"))
        assert result["evidence_id"] in observed
    else:
        assert result["status"] in ("pending", "needs_review") and "total" not in result
    print(f'{path.name}: {len(official_ids)} official cases, {result["functional_points"]}/60, {result["status"]}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    paths = parser.parse_args().files or sorted((ROOT / "evidence").glob("*.json"))
    if not paths:
        sys.exit("No evidence files found.")
    for path in paths:
        verify(path)
