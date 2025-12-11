---
description: Run a command; if it fails, diagnose and make minimal changes until it succeeds (bounded retries).
argument-hint: <command to run>
allowed-tools: Bash(just:*), Bash(npm:*), Bash(pnpm:*), Bash(node:*), Bash(pip:*), Bash(pytest:*), Bash(python:*), Bash(go:*), Bash(git:*), Bash(gradle:*), Bash(java:*)
---

# /debug — auto-fix until it passes

**Command to run (verbatim):** `$ARGUMENTS`

## Policy
- Treat `$ARGUMENTS` as the exact shell command to execute.
- If it **fails**, then analyze stderr/exit code, then iterate. Do this in a loop.
- Freely make small edits, but present a plan and ask permission before making a larger change.
- Keep a running log of each attempt (command, exit status, key changes).
- If you are continuously cycling through the same errors without making progress, stop and report.
- On success: summarize fixes and follow-ups. On failure: summarize highest-leverage next steps.

## Execution steps
1) Run the command with the Bash tool exactly as provided: `$ARGUMENTS`
2) If non-zero exit:
    - Parse errors and identify likely root cause.
    - Apply minimal edits (tests/code/config) with clear diffs.
    - Rerun the command.
3) If you begin continuously repeating or cycling through the same errors without making progress, stop and report.
