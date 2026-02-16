---
description: Multi-pass iterative PR review that discovers layered issues a single pass misses
allowed-tools: Read, Glob, Grep, Write, Bash(bd:*)
---

# Multi-Pass PR Code Review

You are conducting an iterative, multi-pass code review of a pull request. A single-pass review naturally focuses on the most prominent issues (the "top layer"), which means deeper issues only become visible once the top layer is mentally resolved. This command runs multiple review passes, each building on the findings of prior passes, to discover the full set of issues without requiring fixes between iterations.

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

### Phase 2: Iterative Deep Review (Review Analyst × N Passes)

Run the review analyst in a loop of up to **4 passes**. Each pass builds on all prior findings. Maintain a cumulative list of all findings discovered across passes.

#### Pass 1 (Standard Review)

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

Add the findings to the cumulative list.

#### Passes 2-4 (Deeper Review with Cumulative Context)

For each subsequent pass, spawn the `review-analyst` agent (opus) with the same standard inputs as Pass 1, **plus** the following additional context block appended to the prompt:

```
## Multi-Pass Review Context

This is pass N of a multi-pass iterative review. The previous passes have already
identified the following findings:

[Insert cumulative findings list here — one line per finding with file:line, category,
priority (as assigned by the pass that found it), and brief description]

These findings are already captured and will appear in the final consolidated report.
Do NOT re-report them or report variations of them. Instead:

- Look for issues the previous passes overlooked entirely.
- Consider what becomes visible when you treat the above findings as "already solved" —
  what is the next layer of concerns?
- If any of your new findings are **downstream consequences** of a prior finding — meaning
  fixing the prior finding would likely eliminate or fundamentally change this issue — note
  the dependency explicitly, e.g.: "[Depends on finding #3] The caller doesn't handle..."
  This helps the consolidation phase set correct fix ordering.
- [Insert pass-specific emphasis hint — see below]

Apply the same budget philosophy within this pass. Finding 0 new issues is a valid
outcome — it means the previous passes were thorough.
```

**Pass-specific emphasis hints:**

- **Pass 2:** "Pay particular attention to cross-file interactions, implicit contracts between modules, error propagation paths, and assumptions in glue code that connects the changed components."
- **Pass 3:** "Take an adversarial perspective. What would an attacker exploit? What happens when dependencies return unexpected values? What invariants are assumed but never asserted? What race conditions could occur under concurrent access?"
- **Pass 4:** "Final sweep. Check areas not covered by previous passes. Consider: misleading names or documentation where it genuinely confuses, test coverage implications, and any remaining subtle logic gaps in the changed code."

Add each pass's new findings to the cumulative list.

#### Convergence Judgment (After Each Pass)

After each pass completes, **you** (the orchestrator) evaluate whether the review is converging:

1. Look at the new findings from this pass alongside ALL findings from prior passes.
2. Judge the **absolute substantiveness** of the new findings — not the priority labels the analyst assigned. The analyst assigns priorities *relative to what it sees in that pass*, so a "High" finding in pass 3 (after the real issues are excluded) may actually be less important than a "Medium" from pass 1.
3. Ask: are these new findings genuinely different concerns that matter, or are they scraping the bottom of the barrel?

**Stop the loop** when either:
- The new findings are not substantively important compared to the cumulative set (convergence)
- 4 passes have completed (cost cap)

**After each pass, display a brief status update:**
```
Pass N complete: X new findings.
Total across all passes: Y findings.
[If stopping: "Review has converged — proceeding to consolidation."]
[If continuing: "New findings are substantive — continuing to pass N+1."]
```

### Phase 3: Consolidation and Absolute Reprioritization

After the loop completes, consolidate all findings from all passes:

1. **Deduplicate**: If multiple passes found the same concern (same file + same issue), keep the version with the most detailed description. If findings describe the same pattern in different files, keep them as separate findings but note the shared pattern.

2. **Resolve downstream dependencies**: Some later-pass findings may be marked as downstream consequences of earlier findings (e.g., "[Depends on finding #3]"). For each such finding, decide:
   - **Keep it** if it represents a genuinely separate concern that would need its own fix even after the parent is resolved (note the dependency for beads ordering).
   - **Drop it** if fixing the parent finding would eliminate this issue entirely.
   - **Merge it** into the parent finding's description if it adds useful context about the impact of the parent issue but isn't a separate fix.

3. **Reprioritize on an absolute scale**: Each pass's analyst assigned priorities relative to what it saw in that pass. Now that you have the full picture, assign final priorities on an absolute scale:
   - **Urgent**: Bugs and security vulnerabilities that will cause harm in production
   - **High**: Design issues and intent contradictions with compounding cost
   - **Medium**: Logic gaps under realistic edge conditions
   - **Low**: Improvements (naming, style, simplification, performance)

4. **Validate each finding**: Read the relevant code yourself to confirm the finding is real. Drop anything you can't confirm.

5. **Apply the budget**: Even across multiple passes, the budget philosophy applies to the consolidated set:
   - Keep all Urgent and High findings
   - Include Medium findings only if they're actionable and specific
   - Include Low findings only if there are very few higher-priority issues
   - If you'd be left with 0 findings, that's a valid outcome — say so

6. **Ask the user** via `AskUserQuestion` for scope control:
   ```
   Multi-pass review complete (N passes, M findings after deduplication):
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

#### Review Methodology

```
## Review Methodology

This report was generated using a multi-pass iterative review (N passes).
Each pass built on prior findings to discover progressively deeper issues.

| Pass | New Findings | Emphasis |
|------|-------------|----------|
| 1    | X           | General review |
| 2    | Y           | Cross-file interactions, implicit contracts |
| 3    | Z           | Adversarial perspective |
| Total (after dedup) | T | — |
```

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

#### `path/to/file.py:42` — [Bug] Brief one-line description [Pass 1]

Detailed explanation of the issue, including why it's problematic and what scenarios would trigger it.

```python
# Problematic code snippet
```

**Suggestion:** Concrete, actionable fix with code example if applicable.

---
```

The `[Pass N]` attribution after each finding title indicates which review pass discovered it.

#### Notes Section

Include:
- Overall assessment: is this PR well-designed? Does it accomplish its stated goal?
- Positive feedback on well-implemented aspects
- Broader observations about patterns across the PR
- How many passes were needed and what that says about the change's complexity
- If no issues found, say so explicitly — a clean review is a valid outcome

### Phase 5: Output

1. **Determine output path:** `docs/notes/reports/review-pr-deep-{BRANCH}-{YYYY-MM-DD-HH-MM}.md`
   - Extract branch name from context above
   - Use today's date and time

2. **Save report:**
   - Create `docs/notes/reports/` directory if it doesn't exist
   - Write the full report to the output file
   - Confirm the file was written

3. **Display summary** in conversation:
   - Show the review methodology table (passes and findings per pass)
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
bd create "Deep PR Review: <branch> (<YYYY-MM-DD-HH-MM>)" -t epic -p 2 \
  -d "Review report: docs/notes/reports/review-pr-deep-<branch>-<YYYY-MM-DD-HH-MM>.md" --json
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

**Planning label:** Add `-l plan:skip` when **all** of these are true:
- The suggestion is fully prescriptive — it specifies exactly what code to change and how
- The fix affects 1-2 files at most
- No design decisions or trade-offs to evaluate
- Examples: fix an off-by-one error, add a missing null check, rename a misleading variable, add input validation at a specific location

Do **not** add `plan:skip` when:
- The finding is a design issue (wrong abstraction, tight coupling, separation of concerns)
- The fix requires understanding cross-file dependencies
- The suggestion is directional rather than prescriptive (e.g., "restructure this handler")
- Multiple valid fix approaches exist

When in doubt, omit the label. An unnecessary planning phase wastes less than a failed unplanned execution.

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
# Deep PR Review Complete

## Review Methodology

| Pass | New Findings | Emphasis |
|------|-------------|----------|
| 1    | 5           | General review |
| 2    | 4           | Cross-file interactions, implicit contracts |
| 3    | 2           | Adversarial perspective |
| Total (after dedup) | 10 | — |

## Summary

| Priority    | Design | Bug | Security | Logic | Intent | Improvement | Total |
|-------------|--------|-----|----------|-------|--------|-------------|-------|
| Urgent      | 0      | 2   | 1        | 0     | 0      | 0           | 3     |
| High        | 2      | 0   | 0        | 0     | 1      | 0           | 3     |
| Medium      | 0      | 0   | 0        | 3     | 0      | 0           | 3     |
| Low         | 0      | 0   | 0        | 0     | 0      | 1           | 1     |
| **Total**   | 2      | 2   | 1        | 3     | 1      | 1           | 10    |

## Urgent

1. `src/api/auth.py:45` — [Security] SQL injection in user lookup query [Pass 1]
2. `src/services/processor.py:123` — [Bug] Uncaught exception when input is None [Pass 1]
3. `src/api/auth.py:78` — [Bug] Race condition in token validation [Pass 1]

## High

4. `src/services/processor.py:30-80` — [Design] Single method handles validation, transformation, and persistence [Pass 1]
5. `src/api/routes.py:15-40` — [Design] Route handler contains business logic that belongs in service layer [Pass 2]
6. `src/models/user.py:1-15` — [Intent] Module docstring describes authentication but module handles profile management [Pass 1]

Full report saved to: `docs/notes/reports/review-pr-deep-add-auth-2026-01-23-14-30.md`
```

## Related Commands

After reviewing, use these commands to act on findings:
- `/review-pr` — Single-pass review for quick feedback
- `/pr-reply` — Address and resolve PR review comments with code changes
- `/ci-fix` — Debug and fix failing CI workflows on this PR
- `/fix <command>` — Fix specific issues identified in the report (e.g., `/fix just test`)
