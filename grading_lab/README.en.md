# Bilingual Python assignments for a grading agent

This pack contains three assignments with 15 synthetic student solutions each. Each solution has an English and a Traditional Chinese edition, for 45 distinct submissions and 90 files. Paired editions have identical executable logic, IDs, test inputs and required outputs. Prompts, rubrics, source comments and instructor diagnoses are localized.

| Folder | Assignment | Concepts |
|---|---|---|
| 01_scores | Score summary | Empty input, inclusive threshold, duplicate scores, precision |
| 02_parking | Parking fee | Partial hours, cumulative tiers, cap and timeout |
| 03_words | Most frequent word | Tokenization, case, ties and empty input |

## Run a grading session

1. Start in `en/01_scores/`. Give the agent `assignment.md`, `rubric.json` and one file from `submissions/`.
2. The test tool reads `official_tests.json`. Start a fresh student process per case and pass the exact `stdin` string. Collect stdout, stderr and exit status. After a successful exit compare stdout with `expected_stdout`. Normalize line endings and ignore at most one final newline on either side. All other whitespace, case and field order matter. Verification used a one-second timeout per process; budget container startup time separately. One parking submission contains a nonterminating loop for partial hours. Terminate the process or container on timeout.
3. Each of the ten official cases earns six functional points. The three additional cases in `diagnostic_tests.json` help explain observed behavior. Award up to 25 algorithm, 10 specification and 5 readability points using the rubric and cited evidence.
4. After grading, check the matching assignment and submission ID under `teacher_only/en/`. Each record gives the observed per-case results, functional score and intended diagnosis. Keep this directory outside the agent's accessible input during blind evaluation. Each assignment includes a teacher reference program.
5. To compare languages, use a fresh session with the matching ID under `zh-Hant/`, the translated rubric and the same model settings. Compare tool choices, functional score and evidence in the feedback. Treat each pair as one independent example.

## First demonstration

Use `en/01_scores/submissions/S03.py`. The input `80 70 90` should produce `3 80.00 3`. Then try empty input. Ask the agent to identify the failing operation, cite the evidence and propose one fix. Repeat with the Chinese edition. The main README includes a Podman command for this demonstration.

## Verification

Python 3.12 executed 13 cases on each of the 90 student programs, giving 1,170 sample executions. Every paired observation matched. Each copy of each reference program passed all 13 cases for its assignment. Test results are observed program behavior. Instructor diagnoses describe the intended solutions and faults. To evaluate the agent itself, separately exercise model unavailability and the diagnostic-call limit and record actual decision traces.
