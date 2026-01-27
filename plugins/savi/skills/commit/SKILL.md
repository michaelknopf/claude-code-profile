---
description: Commit changes with a contextual message
argument-hint: "[commit message hint]"
model: haiku
---

# Commit Changes

## Current Git State

**Current branch:**
!`git rev-parse --abbrev-ref HEAD`

**Status:**
!`git status`

**Staged changes:**
!`git diff --cached`

**Recent commits (for style reference):**
!`git log --format='%s' -5`

## Instructions

Based on the git state above, create a commit.

1. If the current branch is `main`, create a new branch before committing:
   - Generate a descriptive branch name based on the changes
   - Run `git checkout -b <branch-name>`
2. Analyze the changes and draft a commit message that:
   - Summarizes the nature of the changes (new feature, bug fix, refactor, etc.)
   - Focuses on the "why" rather than the "what"
   - Follows the style of recent commits shown above
3. If $ARGUMENTS is provided, use it as guidance for the commit message
4. Create the commit with the message ending with the standard footer
