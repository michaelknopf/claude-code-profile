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
- The agent orchestrates an autonomous two-model loop:
  - **Opus diagnoses** errors and plans fixes
  - **Sonnet implements** the planned fixes
  - Command is re-run, repeat until success or blocked
- On success: summarize fixes and follow-ups. On failure: summarize highest-leverage next steps.

## Execution steps
1) Run the command with the Bash tool exactly as provided: `$ARGUMENTS`
2) If non-zero exit:
    - Spawn the `fix-loop` agent with the command and initial error output
    - The agent will orchestrate the two-model loop:
      - Spawn opus fix-diagnostician to analyze errors and plan fixes
      - Spawn sonnet implementation agent to apply the planned edits
      - Re-run the command to verify
      - Track attempts and detect cycling (same errors repeating)
      - Return a concise summary when done (success or blocked)
3) Report the agent's summary to the user
