"""Podman integration checks for student outcomes and diagnostic-tool independence."""
import unittest

from grade import ROOT, TestTools, execute, load_cases


class WorkerTests(unittest.TestCase):
    def test_official_outcomes(self):
        for task, sample, case_id, expected in [
            ("01_scores", "S01", "T01", "pass"), ("01_scores", "S03", "T02", "runtime_error"),
            ("01_scores", "S14", "T01", "syntax_error"), ("03_words", "S02", "T05", "wrong_output"),
            ("02_parking", "S13", "T03", "timeout"),
        ]:
            with self.subTest(task=task, sample=sample, case=case_id):
                folder = ROOT / "grading_lab" / "en" / task
                source = (folder / "submissions" / (sample + ".py")).read_text(encoding="utf-8")
                case = load_cases(folder / "official_tests.json")[case_id]
                self.assertEqual(execute(source, case)["status"], expected)

    def test_probe_only_reads_a_teacher_case(self):
        folder = ROOT / "grading_lab/en/01_scores"
        tools = TestTools((folder / "submissions/S03.py").read_text(encoding="utf-8"), {},
                          load_cases(folder / "diagnostic_tests.json"))
        self.assertEqual(tools.call("run_probe", "D01")["status"], "runtime_error")
        with self.assertRaises(ValueError):
            tools.call("run_probe", "D01")
        with self.assertRaises(ValueError):
            tools.call("run_probe", "unknown")


if __name__ == "__main__":
    unittest.main()
