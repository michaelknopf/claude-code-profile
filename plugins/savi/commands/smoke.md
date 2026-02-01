---
description: Design or audit smoke tests using principles
argument-hint: "<design|audit> [target]"
---

# Smoke Test Assistant

## Smoke Test Principles

!`cat ${CLAUDE_PLUGIN_ROOT}/docs/smoke-test-principles.md`

---

## Your Task

**Arguments:** $ARGUMENTS

### Mode: `design`

If the first argument is `design`:
- Analyze the target feature, service, or codebase area specified
- Identify integration points and configuration that need smoke test coverage
- Design smoke tests following the principles above
- Propose complete flow tests rather than fragmented operations
- Consider deployment contexts (isolated vs live environments)

### Mode: `audit`

If the first argument is `audit`:
- Read the existing smoke tests at the specified path
- Evaluate each test against the principles above
- Identify:
  - Tests that could be consolidated into complete flows
  - Tests that duplicate unit test coverage (should be eliminated)
  - Missing coverage for integration points
  - Cleanup and determinism issues
  - Tests that may not be appropriate for live environments
- Propose specific improvements with rationale

### If no mode specified

Ask the user which mode they want:
- `design` - Create new smoke tests for a feature
- `audit` - Review and improve existing smoke tests
