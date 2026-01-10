---
description: Run a command; if it fails, diagnose and make minimal changes until it succeeds (bounded retries).
argument-hint: <command to run>
allowed-tools: Bash(just:*), Bash(npm:*), Bash(pnpm:*), Bash(node:*), Bash(pip:*), Bash(pytest:*), Bash(python:*), Bash(go:*), Bash(git:*), Bash(gradle:*), Bash(java:*)
---

# /debug — auto-fix until it passes

**Command to run (verbatim):** `$ARGUMENTS`

## Policy
- Treat `$ARGUMENTS` as the exact shell command to execute.
- If it **fails**, delegate the fix loop to the `fix-loop` agent
- The agent will analyze, fix, and retry until success or blocked
- Freely make small edits, but present a plan and ask permission before making a larger change.
- On success: summarize fixes and follow-ups. On failure: summarize highest-leverage next steps.

## Execution steps
1) Run the command with the Bash tool exactly as provided: `$ARGUMENTS`
2) If non-zero exit:
    - Spawn the `fix-loop` agent with the command and initial error output
    - The agent will:
      - Parse errors and identify likely root cause
      - Apply minimal edits (tests/code/config)
      - Rerun the command
      - Track attempts and detect if cycling through same errors
      - Return a concise summary when done (success or blocked)
3) Report the agent's summary to the user
