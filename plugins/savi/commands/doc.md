---
description: Create conceptual documentation for code/modules
argument-hint: <path> [--output=<file>]
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion
---

# /doc — Generate Conceptual Documentation

Create high-level conceptual documentation for a file or folder, focusing on the "why" rather than the "what" or "how to use".

## Arguments

**`$ARGUMENTS`**: Target path and optional output location

Parse from `$ARGUMENTS`:
- **Target path** (required) - File or folder to document (e.g., `src/api/`, `lib/parser.py`)
- **`--output=<file>`** (optional) - Specific output location (e.g., `--output=docs/api.md`)

Examples:
```
/doc src/api/
/doc lib/parser.py --output=docs/parsing-architecture.md
/doc plugins/savi/commands/
```

## The Stability Test

Before including ANY detail, ask: **Would this need updating if someone added a new [file/role/config/type/endpoint]?**

- If YES → Don't include it. Stay conceptual, or if specifics are truly needed, link to source rather than inlining.
- If NO → It's likely a stable concept worth documenting.

**Concepts are stable. Implementations change daily.**

A section listing "Available IAM Roles" will break when someone adds a role. A section explaining "How IAM policies are structured and why" remains valid regardless of which specific roles exist.

## What This Command Creates

**This is NOT:**
- A usage guide or manual
- An API reference
- A function/class index
- A code walkthrough
- A duplicate of information that lives in the code itself (enum lists, directory structures, class definitions)
- **A catalog of what currently exists** (all roles, all files, all configs)
- **Content that enumerates instances** (listing each policy type, each endpoint, each module)

**This IS:**
- A conceptual explanation of purpose and motivation
- High-level architectural overview
- Explanation of key abstractions and how they fit together
- Design decisions and their rationale
- Links to relevant source files for implementation details

## Phase 1: Parse Arguments

Extract from `$ARGUMENTS`:
1. **Target path** (required) - What to document
2. **Output location** (optional) - If `--output=<file>` is present, use that path

## Phase 2: Explore Target

Read and understand the code:
- For **folders**: Use Glob to find relevant files, Grep to understand structure, Read key files
- For **files**: Read the file(s) and related context
- Understand: purpose, responsibilities, key abstractions, relationships with other components

## Phase 3: Brief & Clarify

Present your understanding to the user and ask clarifying questions.

**Template:**
```
I've explored [target]. Here's my understanding:

[2-3 paragraph summary of what you learned]

Questions before I write the documentation:
1. [Clarifying question about purpose/scope]
2. [Question about any ambiguous design decisions]
3. [Question about audience or focus areas]
```

Use `AskUserQuestion` tool to gather responses.

## Phase 3.5: Plan Review (Internal Critique)

Before writing, critically evaluate your documentation plan.

**Switch to Critical Reviewer persona.** Your job is to interrogate the plan and catch violations of the stability principles. For each planned section, ask:

1. **Stability Test**: Would this section need updating if someone added a new file/role/config/type? If yes, flag it.
2. **Concept vs. Catalog**: Is this section explaining *how something works* or *listing what exists*? Catalogs fail review.
3. **Maintenance Burden**: Will this section become stale with routine code changes? If yes, flag it.

**Review checklist:**
- [ ] No sections that enumerate "all X" (all roles, all files, all configs)
- [ ] No headers like "Available Types", "Configuration Parameters", "Supported Options"
- [ ] Every section passes the stability test
- [ ] If specifics are needed, they link to source rather than being inlined (but links are optional - prefer staying conceptual)

**If any section fails review:** Rewrite the plan at a higher conceptual level before proceeding. Do NOT proceed to writing until all sections pass.

**Resume Doc Planner persona** with the revised plan.

## Phase 4: Determine Output Location

**If `--output` was specified:** Use that path exactly.

**If no `--output` specified:** Choose the best location based on context.

Options:
1. **Adjacent to target** - Co-locate with what's being documented
   - For self-contained modules/packages
   - Example: `src/api/` → `src/api/README.md` or `src/api/API.md`

2. **Centralized docs folder** - Place in `docs/` directory
   - For cross-cutting concerns
   - For high-level architectural documentation
   - If project already has similar docs in `docs/`
   - Example: `src/api/` → `docs/api-architecture.md`

**Important:** Never use `docs/notes/` (typically gitignored)

Choose a descriptive filename that reflects the content:
- `README.md` for module overviews
- `[Component].md` for specific components (e.g., `API.md`, `Parser.md`)
- `[topic]-[aspect].md` for focused docs (e.g., `auth-architecture.md`)

## Phase 5: Write Document

### Structure and Organization

**Think carefully about structure.** Don't force a rigid template. Instead, consider:
- What mental model would most help someone understand this?
- What's the natural progression from "I know nothing" to "I understand how this works"?
- What sections would make this most scannable and navigable?

**Common patterns** (use what fits, skip what doesn't):
- **Purpose/Overview**: Why this exists, what problem it solves
- **Key Concepts**: Core abstractions and mental models
- **Architecture/How It Works**: How pieces fit together
- **Design Decisions**: Important choices and trade-offs
- **Examples/Illustrations**: Concrete scenarios that clarify abstract concepts

Let the content guide the structure. A data pipeline might benefit from a "Data Flow" section. A state machine might need "State Transitions." An integration layer might need "Contracts and Boundaries."

### Document Format

```markdown
# [Module/Component Name]

> **Note:** This document provides conceptual explanations with illustrative code examples. For current implementation details, refer to the linked source files. Examples may evolve over time.

[Your thoughtfully structured content here]

---

## Generation Metadata

**Generated by:** `/doc` command
**Date:** [YYYY-MM-DD]
**Source paths:**
- [path/to/file1]
- [path/to/folder/]

**Additional context:** [Any clarifying information from user Q&A, or "None" if no additional context]
```

### Writing Guidelines

**Audience:**
Write for someone who has just joined the project and is trying to orient themselves. They need to understand where this fits, why it exists, and how it works conceptually before diving into the code. Help them build the right mental model.

**Content:**
- **Focus on "why" over "what"**: Explain purpose and rationale, not implementation details
- **Minimal code snippets**: Only include code if it helps explain a concept, not as examples of usage
- **High-level**: Stay at the conceptual/architectural level, avoid line-by-line explanations
- **Self-sufficient**: Document should be understandable without reading the code
- **Avoid instruction**: This is not a "how to use" guide

**✗ DO NOT:**
- Create sections that list "all X" (all files, all types, all configs, all roles)
- Write content requiring updates when someone adds a new instance of something
- Document *what exists* instead of *why it exists and how it works*
- Use headers like "Available Types", "Supported Options", "Configuration Parameters"

### Code Duplication Guidelines

**Don't inline code/lists that will become stale:**
- Never inline full enum lists, class definitions, or config structures
- If you must reference specifics, link to source rather than inlining (but prefer staying conceptual)
- Example: "The system recognizes various entity types including PHONE_NUMBER, EMAIL, and CRYPTO_ADDRESS. See `src/models/entities.py` for the complete list." (only if the specifics add value)

**Examples, not exhaustive lists:**
- When showing examples (enum values, entity types, etc.), show 2-4 illustrative ones at most
- Always note that examples may evolve
- Best: Stay conceptual and don't enumerate at all

**Never include directory structures:**
- Directory tree listings are maintenance nightmares and duplicate what's visible in the file tree
- If you need to reference file locations, mention specific paths in text or link directly

**When code snippets ARE appropriate:**
- Explaining a concept that requires seeing the structure (e.g., how state flows through a system)
- Showing a stable interface/contract that's central to understanding
- The code is unlikely to change frequently
- Always include a disclaimer that examples are illustrative

### Avoiding Reference-Style Documentation

**Bad - Enumeration disguised as documentation:**
> ## Available Policy Types
> The module supports the following IAM policies:
> - `admin-access`: Full administrative access
> - `read-only`: Read-only access to resources
> - `deployment`: CI/CD deployment permissions
> [... 10 more items ...]

**Good - Conceptual explanation:**
> ## Policy Architecture
> The module uses a policy-per-role pattern where each IAM role has a dedicated policy file. Policies are structured around the principle of least privilege, granting only the permissions required for each role's specific function. See `policies/` for the current policy definitions.

---

**Bad - Configuration as reference:**
> ## Configuration
> The module accepts these inputs:
> - `environment`: The deployment environment (dev/staging/prod)
> - `region`: AWS region
> - `enable_logging`: Whether to enable CloudWatch logging
> [... 15 more items ...]

**Good - Configuration concepts:**
> ## Configuration Model
> The module is configured through a single YAML file that defines the environment, regional settings, and feature flags. Required settings are validated at plan time. See `variables.tf` for the full input specification.

## Phase 5.5: Final Review (Document Quality)

Before saving, switch to **Document Reviewer** persona. Review the complete document holistically for usefulness and organization:

**Usefulness check:**
- Is this document useful for the intended audience?
- Does each section add conceptual value? If a section isn't pulling its weight, either omit it or move it to an appendix if it's borderline/feels out of place.

**Organization check:**
- Does information flow logically? Each section should build on concepts established in earlier sections.
- Is any section confusing until you've read a later section? That's a sign of poor organization - reorder so foundational concepts come first.
- Would a reader need to jump around to understand the document, or can they read top-to-bottom?

**If the document fails these checks:** Reorganize, trim, or add an appendix as needed before saving.

## Phase 6: Save

Write the document to the chosen/specified location.

Confirm to the user:
```
Documentation created at: `[path/to/output.md]`
```

## Important Notes

- **Must include metadata section**: The `/doc-refresh` command relies on this to update the doc later
- **Be judicious with location choice**: Consider project structure and existing documentation patterns
- **Ask questions**: Use `AskUserQuestion` to clarify before writing - better to confirm than assume

## Examples

### Example 1: Document a folder
```
/doc src/api/
```
Explores the API module, asks clarifying questions, generates documentation at either `src/api/README.md` or `docs/api-architecture.md` depending on context.

### Example 2: Document a specific file with custom output
```
/doc lib/parser.py --output=docs/parser-design.md
```
Documents the parser module, saves to specified location.

### Example 3: Document the commands folder itself
```
/doc plugins/savi/commands/
```
Generates conceptual documentation explaining the command system architecture.
