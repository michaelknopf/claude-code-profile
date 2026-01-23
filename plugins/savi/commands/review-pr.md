---
description: Review the current branch's PR diff and produce an audit report
argument-hint: "[--output=<file>] [--no-save]"
allowed-tools: Read, Glob, Grep, Write
---

# PR Code Review

You are conducting a code review of a pull request. Your task is to analyze the diff against main and produce a prioritized audit report of issues found.

## Current Context

**Branch:** `!git rev-parse --abbrev-ref HEAD`

**PR Details:**
```
!gh pr view --json title,body,labels,url 2>/dev/null || echo "No PR found - reviewing branch diff"
```

**Diff Statistics:**
```
!git diff main...HEAD --stat
```

**Changed Files:**
```
!git diff main...HEAD --name-only
```

## Issue Categories

Classify each finding into one of these categories:

- **Bug**: Logic errors, incorrect behavior, race conditions, off-by-one errors, null handling issues
- **Security**: Injection vulnerabilities, auth bypass, data exposure, insecure defaults, missing validation
- **Design**: Wrong abstraction, tight coupling, separation of concerns violations, poor API design
- **Logic**: Works on happy path but breaks under edge conditions, incorrect assumptions
- **Naming**: Misleading names, unclear intent, names that don't match actual behavior
- **Style**: Formatting issues, project convention inconsistency, code organization
- **Simplification**: Over-engineering, unnecessary complexity, could be shorter or clearer
- **Performance**: Inefficient algorithms, N+1 queries, unnecessary allocations (only when meaningful impact)

## Priority Levels

Assign each finding a priority:

- **High**: Bugs, security issues, logic errors that will cause failures in production
- **Medium**: Design issues, confusing naming, meaningful performance problems
- **Low**: Style inconsistencies, simplification opportunities that don't affect correctness

## Review Process

### Phase 1: Parse Arguments

Parse the command arguments:
- `--output=<file>`: Custom output file path (relative to repo root)
- `--no-save`: Display report in conversation only, don't save to file

### Phase 2: Gather Full Context

1. **Read the complete diff**:
   ```bash
   git diff main...HEAD
   ```

2. **Read all changed files** to understand surrounding context (not just the diff lines)

3. **Understand PR intent** from:
   - PR title and description
   - Commit messages: `git log main..HEAD --oneline`
   - Any referenced issues or design docs

### Phase 3: Review Each Change

For every change in the diff:

1. **Examine the code** against all issue categories
2. **Consider the PR's intent** - don't criticize the chosen approach if it's appropriate for the stated goal
3. **Focus on new code** - ignore pre-existing patterns unless this PR makes them worse
4. **Apply confidence threshold** - only report issues you're confident about (no false positives)
5. **Be constructive** - every finding must include a concrete, actionable suggestion

**Key principles:**
- Skip uncertain findings - better to miss a minor issue than report false positives
- Don't nitpick trivial style issues unless they genuinely harm readability
- Consider whether an issue is introduced by this PR or pre-existing
- Provide code snippets and specific line numbers for each finding
- Explain WHY something is an issue, not just WHAT is wrong

### Phase 4: Compile Report

Generate a structured markdown report with:

#### Summary Table

```
| Priority | Bug | Security | Design | Logic | Naming | Style | Simplification | Performance | Total |
|----------|-----|----------|--------|-------|--------|-------|----------------|-------------|-------|
| High     | 0   | 0        | 0      | 0     | 0      | 0     | 0              | 0           | 0     |
| Medium   | 0   | 0        | 0      | 0     | 0      | 0     | 0              | 0           | 0     |
| Low      | 0   | 0        | 0      | 0     | 0      | 0     | 0              | 0           | 0     |
| **Total**| 0   | 0        | 0      | 0     | 0      | 0     | 0              | 0           | 0     |
```

#### Findings by Priority

Group findings by priority (High → Medium → Low), then by file. For each finding:

```markdown
### High Priority

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
- Broader observations about patterns across the PR
- Positive feedback on well-implemented changes
- Suggestions for follow-up refactoring (if any)
- Overall assessment of code quality

### Phase 5: Output

1. **Determine output path:**
   - If `--output=<file>` provided, use that path (relative to repo root)
   - Otherwise, use `docs/notes/review-pr-{BRANCH}-{YYYY-MM-DD}.md`
     - Extract branch name from Phase 2
     - Use today's date in ISO format

2. **Save report** (unless `--no-save` flag is present):
   - Create `docs/notes/` directory if it doesn't exist
   - Write the full report to the output file
   - Confirm the file was written

3. **Display summary** in conversation:
   - Show the summary table
   - List high-priority findings (brief)
   - Include the file path where the full report was saved
   - If `--no-save`, display the complete report in the conversation

## Example Output (Conversation)

```
# PR Review Complete

## Summary

| Priority | Bug | Security | Design | Logic | Naming | Style | Simplification | Performance | Total |
|----------|-----|----------|--------|-------|--------|-------|----------------|-------------|-------|
| High     | 2   | 1        | 0      | 1     | 0      | 0     | 0              | 0           | 4     |
| Medium   | 0   | 0        | 3      | 0     | 2      | 0     | 1              | 0           | 6     |
| Low      | 0   | 0        | 0      | 0     | 0      | 4     | 2              | 0           | 6     |
| **Total**| 2   | 1        | 3      | 1     | 2      | 4     | 3              | 0           | 16    |

## High Priority Issues

1. `src/api/auth.py:45` — [Security] SQL injection vulnerability in user lookup
2. `src/services/processor.py:123` — [Bug] Uncaught exception when input is None
3. `src/api/auth.py:78` — [Bug] Race condition in token validation
4. `src/utils/parser.py:34` — [Logic] Integer overflow on large inputs

Full report saved to: `docs/notes/review-pr-add-auth-2026-01-23.md`
```

## Important Notes

- **No false positives**: Only report issues you're genuinely confident about
- **Context matters**: Understand the PR's goal before criticizing implementation choices
- **Be specific**: Include file paths, line numbers, code snippets, and concrete suggestions
- **Stay objective**: Focus on technical merit, not style preferences (unless they impact readability)
- **Acknowledge good work**: If the PR is well-implemented, say so in the Notes section
