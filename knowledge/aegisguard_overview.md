# How AegisGuard works

## The loop
AegisGuard takes a vulnerable Python app through six steps. Triage scans the code and finds the risky function and the public route that reaches it. The exploit agent writes a test that attacks the bug. The sandbox runs that test, and it must fail for the right reason, which proves the bug is real. The patch agent writes a fix. The verifier runs the attack test and the existing regression tests again on the fixed code. Finally a human reviews the change and approves it.

## How a fix is verified
A fix only counts when two things are true: the attack test now passes, and all the original regression tests still pass. AegisGuard also scans the fixed code again to check the risky pattern is gone. If verification fails, the patch agent retries with the failure output, up to a limit of three attempts, and then the case is escalated to a human.

## Why the exploit test is checked
The attack test is written by an AI, so it could fail for the wrong reason, such as an import error. AegisGuard checks that the failure is an assertion failure inside the exploit test and not a setup error before it accepts the result.

## Sandbox
Tests run in a sandbox. In Docker mode the container has no network, limited memory and CPU, and a non-root user. In local mode the tests run directly on the computer, which is faster to set up but not isolated.

## Retrieval and memory
Before patching, AegisGuard retrieves short security notes from its knowledge base and gives them to the patch agent (retrieval-augmented generation, or RAG). Every run is also saved in long-term memory, so later runs can reuse a verified fix and avoid past mistakes.

## Human approval
AegisGuard never applies a change on its own. A person reviews the diff and the green verification result and clicks approve. Approved patches are saved to a file.

## Limits
The scanner recognizes three patterns: SQL injection, path traversal and cross-site scripting. It works on the sample apps provided, not on arbitrary projects. AI output varies between runs, so some runs need a retry or are escalated. Opening a GitHub pull request is not implemented yet.