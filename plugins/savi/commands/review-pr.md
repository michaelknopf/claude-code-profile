---
description: Review the current branch's PR diff and produce a prioritized audit report
allowed-tools: Read, Glob, Grep, Write, Bash(bd:*)
---

# PR Code Review

You are conducting a code review of a pull request. Your task is to deeply understand the change, then produce a prioritized audit report focused on design, correctness, and logic — not style or implementation minutiae.

## Code Review Principles

!`cat ${CLAUDE_PLUGIN_ROOT}/docs/code-review-principles.md`

---

## Current Context

**Branch:** `!git rev-parse --abbrev-ref HEAD`

**PR Details:**
```
!gh pr view --json title,body,labels,url 2>/dev/null || echo "No PR found - reviewing branch diff"
```

**Commit History:**
```
!git log main..HEAD --oneline
```

**Diff Statistics:**
```
!git diff main...HEAD --stat
```

**Changed Files:**
```
!git diff main...HEAD --name-only
```

## Review Process

### Phase 1: Understand Intent (Review Scout)

Spawn the `review-scout` agent (sonnet) to perform a fast first pass. Pass it:
- The PR metadata from the context above (title, description, labels, commit messages)
- The changed file list and diff statistics
- The changed files themselves (for structural scanning)

The agent will return:
- **Intent summary**: What this PR does and why
- **Structural overview**: Shape of the change at a high level
- **Context gaps**: Areas where intent is unclear

If the agent reports context gaps, use `AskUserQuestion` to seek clarification before proceeding. Ask about:
- What problem this PR is solving
- Any constraints or tradeoffs the author is working within
- Whether this is part of a larger effort

**Do not proceed to Phase 2 until intent is clear.**

### Phase 2: Deep Review (Review Analyst)

Spawn the `review-analyst` agent (opus) to perform the detailed analysis. Pass it:

- The intent summary and structural overview from Phase 1 (plus any clarifications from the user)
- The full diff (`git diff main...HEAD`)
- The changed file list
- The code review principles (already loaded above)
- Project conventions from `~/.claude/CLAUDE.md` and project-level `CLAUDE.md`

The agent will:
1. Read full files for context (not just diff hunks)
2. Check for contradictions between intent and implementation
3. Review design: abstractions, responsibilities, architectural fit, API surface, extensibility, coupling
4. Review correctness and security: bugs, trust boundaries, injection vectors, error paths
5. Review logic: realistic edge conditions the code doesn't handle
6. Note improvements only if few substantive issues found
7. Return a prioritized inventory of findings

### Phase 3: Prune and Reprioritize

Review the reviewer agent's findings and apply the budget:

1. **Validate each finding**: Read the relevant code yourself to confirm the finding is real. Drop anything you can't confirm.

2. **Reprioritize**: Adjust priorities if needed:
   - **Urgent**: Bugs and security vulnerabilities that will cause harm in production
   - **High**: Design issues and intent contradictions with compounding cost
   - **Medium**: Logic gaps under realistic edge conditions
   - **Low**: Improvements (naming, style, simplification, performance)

3. **Apply the budget**: If the PR is generally well-designed:
   - Keep all Urgent and High findings
   - Include Medium findings only if they're actionable and specific
   - Include Low findings only if there are very few higher-priority issues
   - If you'd be left with 0 findings, that's a valid outcome — say so

4. **Ask the user** via `AskUserQuestion` for scope control:
   ```
   Found N findings across M files:
   - Urgent: X (bugs/security)
   - High: Y (design/intent)
   - Medium: Z (logic)
   - Low: W (improvements)

   Options:
   - Substantive only (Urgent + High + Medium) [Recommended]
   - Full report (all findings)
   - Urgent and High only
   ```

### Phase 4: Compile Report

Generate a structured markdown report with the user's approved scope.

#### Summary Table

```
| Priority    | Design | Bug | Security | Logic | Intent | Improvement | Total |
|-------------|--------|-----|----------|-------|--------|-------------|-------|
| Urgent      | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
| High        | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
| Medium      | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
| Low         | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
| **Total**   | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
```

#### Issue Categories

- **Design**: Wrong abstraction, tight coupling, separation of concerns violations, poor API surface, architectural misfit
- **Bug**: Logic errors, incorrect behavior, race conditions, boundary condition failures
- **Security**: Injection vulnerabilities, auth bypass, data exposure, missing validation at trust boundaries
- **Logic**: Works on happy path but fails under realistic edge conditions
- **Intent**: Contradictions between documentation/comments/PR description and actual code behavior
- **Improvement**: Naming, style, simplification, performance (only when genuinely impactful)

#### Findings by Priority

Group findings by priority (Urgent → High → Medium → Low). For each finding:

```markdown
### Urgent

#### `path/to/file.py:42` — [Bug] Brief one-line description

Detailed explanation of the issue, including why it's problematic and what scenarios would trigger it.

```python
# Problematic code snippet
```

**Suggestion:** Concrete, actionable fix with code example if applicable.

---
```

#### Notes Section

Include:
- Overall assessment: is this PR well-designed? Does it accomplish its stated goal?
- Positive feedback on well-implemented aspects
- Broader observations about patterns across the PR
- If no issues found, say so explicitly — a clean review is a valid outcome

### Phase 5: Output

1. **Determine output path:** `docs/notes/reports/review-pr-{BRANCH}-{YYYY-MM-DD}.md`
   - Extract branch name from context above
   - Use today's date in ISO format

2. **Save report:**
   - Create `docs/notes/reports/` directory if it doesn't exist
   - Write the full report to the output file
   - Confirm the file was written

3. **Display summary** in conversation:
   - Show the summary table
   - List Urgent and High findings (brief)
   - Include the file path where the full report was saved

### Phase 6: Beads Integration (optional)

After saving the report, use `AskUserQuestion` to ask the user if they want to create beads issues for the findings:

```
Options:
- Yes, create beads issues (Recommended)
- No, skip
```

If the user declines, stop here.

If the user accepts, proceed with beads integration:

#### 6.1: Check Beads Availability

```bash
bd info --json 2>/dev/null
```

If beads is not initialized (command fails), inform the user and skip. Do not proceed with issue creation.

#### 6.2: Create Epic

Create an epic to track the review findings:

```bash
bd create "PR Review: <branch> (<YYYY-MM-DD>)" -t epic -p 2 \
  -d "Review report: docs/notes/reports/review-pr-<branch>-<YYYY-MM-DD>.md" --json
```

Extract the epic ID from the JSON response for use in subsequent steps.

#### 6.3: Create Subtasks

For each finding in the report, create a subtask:

```bash
bd create "<short-title>" -t task -p <priority> --parent <epic-id> \
  -d "**Category:** [<category>]

**Location:** <file:lines>

**Description:** <description>

**Suggestion:** <suggestion>" --json
```

**Priority mapping:**
- Urgent findings → `1`
- High findings → `1`
- Medium findings → `2`
- Low findings → `3`

**Short title format:** `<file> - <brief-description>`
- Example: `auth.py - Fix SQL injection in user lookup`
- Keep titles under 60 characters

Extract task IDs from JSON responses and map them to report finding numbers (e.g., finding #1 → task_id_1).

#### 6.4: Set Dependencies

For findings that should be tackled in a particular order (e.g., a design issue must be fixed before a dependent logic issue):

```bash
bd dep add <prerequisite-task-id> <dependent-task-id> --type blocks
```

**Important:** Only create blocking dependencies. Related tasks that don't block each other should remain independent.

#### 6.5: Sync to Remote

Synchronize the issues to the remote repository:

```bash
bd sync
```

#### 6.6: Report to User

Display a summary of the beads integration:

```
Created epic <epic-id> with N subtasks in beads.

To address these findings:
1. Run `bd ready` to see unblocked tasks
2. Run `/savi:next --loop` in a new session to process all ready tasks automatically
3. Or pick individual tasks with `/savi:next` (processes one at a time)

Track progress:
- `bd stats` - View completion statistics
- `bd blocked` - See tasks waiting on dependencies
- `bd show <epic-id>` - View full epic details
```

## Example Output (Conversation)

```
# PR Review Complete

## Summary

| Priority    | Design | Bug | Security | Logic | Intent | Improvement | Total |
|-------------|--------|-----|----------|-------|--------|-------------|-------|
| Urgent      | 0      | 2   | 1        | 0     | 0      | 0           | 3     |
| High        | 2      | 0   | 0        | 0     | 1      | 0           | 3     |
| Medium      | 0      | 0   | 0        | 2     | 0      | 0           | 2     |
| Low         | 0      | 0   | 0        | 0     | 0      | 0           | 0     |
| **Total**   | 2      | 2   | 1        | 2     | 1      | 0           | 8     |

## Urgent

1. `src/api/auth.py:45` — [Security] SQL injection in user lookup query
2. `src/services/processor.py:123` — [Bug] Uncaught exception when input is None
3. `src/api/auth.py:78` — [Bug] Race condition in token validation

## High

4. `src/services/processor.py:30-80` — [Design] Single method handles validation, transformation, and persistence
5. `src/api/routes.py:15-40` — [Design] Route handler contains business logic that belongs in service layer
6. `src/models/user.py:1-15` — [Intent] Module docstring describes authentication but module handles profile management

Full report saved to: `docs/notes/reports/review-pr-add-auth-2026-01-23.md`
```

## Related Commands

After reviewing, use these commands to act on findings:
- `/pr-reply` — Address and resolve PR review comments with code changes
- `/ci-fix` — Debug and fix failing CI workflows on this PR
- `/fix <command>` — Fix specific issues identified in the report (e.g., `/fix just test`)
