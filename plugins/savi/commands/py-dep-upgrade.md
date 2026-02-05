---
description: Remove upper bounds and upgrade all Python dependencies, fixing issues as needed
argument-hint: "[--dry-run] [<test-command>]"
allowed-tools: Bash(uv:*), Bash(just:*), Bash(pytest:*), Bash(python:*), Bash(git:*), Read, Edit, Glob, Grep, Task
---

# Dependency Upgrade Command

Removes upper bounds from Python dependencies and upgrades to latest versions, fixing any resulting issues.

## Design Philosophy

**Upper bounds are usually unnecessary.** With `uv.lock` pinning exact versions, `pyproject.toml` only needs minimum versions (`>=X.Y.Z`). Upper bounds should only be added when a specific incompatibility is discovered - with detailed comments explaining why.

## Argument Parsing

Parse command arguments:
- `--dry-run` - Show what would change without modifying anything
- `<test-command>` - Command to verify success (default: `just check` or `pytest`)

Store these in variables for use throughout execution.

## Phase 1: Find pyproject.toml

Use Glob to locate `pyproject.toml` in the current directory or parent directories.

## Phase 2: Remove Upper Bounds

Read `pyproject.toml` and identify all dependency specifications with upper bounds.

Remove upper bounds according to these rules:
- `>=X.Y.Z,<A.B.C` → `>=X.Y.Z`
- `^X.Y.Z` → `>=X.Y.Z` (caret syntax implies upper bound)
- `~=X.Y.Z` → `>=X.Y.Z` (compatible release implies upper bound)
- `==X.Y.Z` → `>=X.Y.Z` (exact pin becomes minimum)

If `--dry-run`:
- Display what would change
- Exit successfully

Otherwise, use Edit to make the changes.

## Phase 3: Upgrade Dependencies

Run the upgrade commands:
```bash
uv lock --upgrade
uv sync
```

## Phase 4: Run Checks

Determine the test command:
- Use user-provided command if specified
- Otherwise try `just check`
- Fall back to `pytest` if just doesn't exist

Run the test command to verify everything works.

If tests pass → skip to Phase 6 (Summary).

## Phase 5: Fix Loop

If tests fail, enter a fix loop with a maximum of 10 attempts:

### 5.1 Diagnose

Spawn an Opus agent using the Task tool to analyze the failure:
```
Analyze this test failure after upgrading dependencies.

Failure output:
[paste failure output]

Determine:
1. Is this a breaking API change in a dependency?
2. Is this a type error from updated stubs?
3. Is this a removed/renamed function?
4. What action should we take?
```

### 5.2 Decide Action

Based on the diagnosis, choose one of:

**Option A: Code Fix**
- Adapt code to work with the new dependency version
- Spawn Sonnet agent to implement the fix

**Option B: Add Upper Bound**
- If the upgrade is too disruptive to fix immediately
- Add upper bound with detailed comment explaining why:
  ```python
  "somelib>=1.0,<2.0",  # Pinned: v2.0 removed foo() API, migration requires X
  ```

### 5.3 Implement

Spawn appropriate agent (Sonnet for code changes, or direct Edit for pinning):
```
[For code fix]
Fix the code to work with the upgraded dependency.

Details from diagnosis:
[paste diagnosis]

Make the necessary changes to resolve the test failure.
```

### 5.4 Re-test

Run the test command again.

If tests pass → exit loop and continue to Phase 6.

If tests fail and attempts < 10 → return to 5.1.

If attempts >= 10 → report failure and exit.

## Phase 6: Summary

Report the results:

```
Dependency Upgrade Summary
==========================

Dependencies Upgraded:
- package1: 1.0.0 → 2.1.0
- package2: 3.2.1 → 3.5.0

Upper Bounds Removed:
- package1: >=1.0,<2.0 → >=1.0
- package3: ^2.1.0 → >=2.1.0

Upper Bounds Added:
- package4: >=1.0 → >=1.0,<2.0
  Reason: v2.0 removed deprecated API, requires migration

Code Changes:
- path/to/file.py: Updated to use new API
- other/file.py: Fixed type annotations

Final Status: ✓ All tests passing
```

## Error Handling

- If pyproject.toml not found, exit with clear error
- If uv commands fail, report the error and exit
- If max attempts reached in fix loop, report summary with failure status
