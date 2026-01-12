---
description: Analyze coverage gaps and create prioritized test improvement plan
argument-hint: <coverage.json> [--top=N] [--output=file.md]
allowed-tools: Read, Write, Glob, Grep
---

# /coverage-plan — Test Coverage Planning

**Coverage file:** `$ARGUMENTS`

## Overview

Analyzes a coverage report to create an actionable test improvement plan. Unlike simple coverage metrics, this command:
- Prioritizes gaps by **value** (complexity, business logic) not just line count
- Designs test suites with **purpose and strategy**
- Recommends **mocking approaches** and **refactoring for testability**
- Spawns parallel sub-agents for deep analysis of each coverage gap

## Prerequisites

Generate a coverage report first:
```bash
just coverage
```

## Phase 1: Parse Coverage Data

1. **Parse arguments**:
   - Coverage file path (required)
   - `--top=N` flag (optional, default: 10)
   - `--output=file.md` flag (optional, default: stdout)

2. **Read the coverage JSON**:
   - Expected format: pytest-cov / coverage.py JSON
   - Extract files with missing coverage
   - Identify uncovered line ranges

3. **Initial filtering**:
   - Skip test files (files matching `test_*.py`, `*_test.py`)
   - Skip generated files (migrations, `__pycache__`, etc.)
   - Skip files with >90% coverage (unless user specifies otherwise)

## Phase 2: Assess Value & Prioritize

For each file with coverage gaps:

1. **Read the source code** for the uncovered lines

2. **Assess complexity**:
   - **Line count** of uncovered sections
   - **Branching** (if/else, try/except, loops)
   - **Dependencies** (imports, external calls)
   - **Code type**:
     - High value: Business logic, algorithms, error handling
     - Medium value: Data transformations, integrations
     - Low value: Getters/setters, config loading, boilerplate

3. **Calculate priority score**:
   - Complexity (high branching = higher priority)
   - Business criticality (payment processing > logging)
   - Risk (error-prone areas)

4. **Rank gaps** from highest to lowest value

## Phase 3: User Approval

Present ranked list and ask via `AskUserQuestion`:

```
Found 12 coverage gaps. Top priorities:

Priority 1: src/api/payment.py (45% covered)
  - 15 uncovered lines in process_payment()
  - Complex: error handling, retry logic, state transitions

Priority 2: src/services/inventory.py (60% covered)
  - 22 uncovered lines in allocate_stock()
  - Complex: concurrent updates, transaction handling

Priority 3: src/utils/validators.py (70% covered)
  - 8 uncovered lines in validate_order()
  - Medium: input validation, edge cases

...

How many should I analyze in depth?
- Top 3 (Recommended)
- Top 5
- Top 10
- All 12
```

## Phase 4: Deep Analysis (Parallel Sub-Agents)

For each approved coverage gap, spawn a `test-suite-planner` agent **in parallel** with `model: opus`.

Pass to each agent:
- File path and uncovered line ranges
- The actual source code
- Brief context about what the code does
- Any existing test files for that module

Agents will analyze and return structured test suite designs.

**Important**: Launch all agents in parallel in a single message using multiple Task tool calls with `model: "opus"`. This maximizes efficiency and ensures high-quality test suite designs.

## Phase 5: Compile Report

Combine agent outputs into a prioritized markdown report:

```markdown
# Test Coverage Improvement Plan

Generated: 2025-01-11
Coverage file: coverage.json
Analyzed: 12 gaps, planned: 5 high-priority suites

---

## Priority 1: src/api/payment.py

**Coverage:** 45% (15 uncovered lines in process_payment)

### Purpose
Validates payment processing including authorization, capture, refunds, and error handling.

### Test Cases

**Happy Path:**
1. Successful authorization and capture
2. Immediate capture (skip authorization)
3. Partial and full refunds

**Edge Cases:**
1. Authorization expires before capture
2. Network timeout during API call
3. Insufficient funds handling

**Error Scenarios:**
1. Invalid payment method format
2. Duplicate idempotency key
3. Stripe API errors (5xx)

### Mocking Strategy

**Mock:**
- Stripe API client (external dependency, want predictable responses)
- Database transactions (isolate payment logic from storage)

**Don't Mock:**
- Payment validation logic (core unit under test)
- Amount calculations (pure functions)

### Refactoring Suggestions

**For testability:**
- Extract `PaymentValidator` class for independent validation testing
- Add dependency injection for Stripe client (currently instantiated in method)
- Split `process_payment()` into smaller functions:
  - `_authorize_payment()`
  - `_capture_payment()`
  - `_handle_payment_error()`

**Priority:** High - complex method, hard to test in current form

---

## Priority 2: src/services/inventory.py

**Coverage:** 60% (22 uncovered lines in allocate_stock)

...

---

## Summary

**High Priority:** 2 suites (payment, inventory)
**Medium Priority:** 3 suites (validators, notifications, webhooks)

**Next Steps:**
1. Review and adjust priorities based on business needs
2. Implement refactoring suggestions for high-priority modules
3. Write test suites in priority order
4. Run coverage again to verify improvement
```

## Phase 6: Output

If `--output` flag provided:
- Write report to specified file
- Confirm file path

Otherwise:
- Display report in conversation

## Examples

### Basic usage
```bash
/coverage-plan coverage.json
```

### Focus on top 3
```bash
/coverage-plan coverage.json --top=3
```

### Save to file
```bash
/coverage-plan coverage.json --output=test-plan.md
```

## Coverage JSON Format Reference

Expected structure from pytest-cov:

```json
{
  "meta": {
    "version": "6.5.0",
    "timestamp": "2025-01-11T10:30:00"
  },
  "files": {
    "src/api/payment.py": {
      "executed_lines": [1, 2, 3, 10, 11, 20, 21],
      "missing_lines": [15, 16, 17, 18, 25, 26, 27],
      "excluded_lines": [],
      "summary": {
        "covered_lines": 7,
        "num_statements": 14,
        "percent_covered": 50.0,
        "missing_lines": 7
      }
    }
  },
  "totals": {
    "covered_lines": 450,
    "num_statements": 600,
    "percent_covered": 75.0
  }
}
```

## Guidelines

- **Value over volume**: High-priority complex code > 100% coverage of simple code
- **Parallel agents**: Launch all `test-suite-planner` agents in parallel for speed
- **Actionable output**: Each suite should have clear purpose, cases, and strategy
- **Realistic refactoring**: Don't suggest massive rewrites; focus on testability improvements
- **User control**: Always get approval on scope before spawning agents
