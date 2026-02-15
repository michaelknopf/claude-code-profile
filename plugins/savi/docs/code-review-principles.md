# Code Review Principles

Code review is an analytical discipline. The reviewer's job is not to find fault but to deeply understand a change and assess whether it serves its goal well. Findings emerge from that understanding — not from scanning for checklist violations.

These principles guide what to look for, how to prioritize, and when to hold back.

## Understand Before You Evaluate

The most common failure in code review is evaluating code you haven't understood. A reviewer who jumps straight to line-by-line analysis will flag things that make perfect sense in context and miss things that only become visible from a higher vantage point.

Before reading any code, read the PR description. Read the referenced issues. Read the commit messages. Understand what problem is being solved, what constraints the author is operating under, and what tradeoffs they've chosen. If the PR is part of a larger effort — a migration, a multi-PR feature, a phased rollout — understand where it sits in that arc.

If the PR description is thin or the context is unclear, seek clarification. A reviewer who proceeds without understanding the intent will produce feedback that is technically correct but practically useless — or worse, feedback that pushes the author toward a solution that doesn't fit the constraints they're working within.

Only after you have a mental model of what the change is trying to accomplish should you begin reading code. And even then, start by reading at a high level: the file structure, the flow of control, the shape of the change. Understand the forest before examining the trees.

This ordering matters because it changes what you see. A reviewer who understands that a PR is the first step in decomposing a monolith will read "imperfect" boundaries differently than one who assumes the code should be in its final form. A reviewer who knows the author is working around a third-party limitation will not suggest removing the workaround. Context transforms observation into insight.

## Intent and Implementation Must Agree

As you transition from understanding intent to reading code, pay attention to the documentation layer between them: docstrings, inline comments, prompt templates, configuration descriptions, README sections, and the PR description itself. These artifacts communicate purpose and design intent. When they contradict each other — or contradict the code — that's a finding.

Not all contradictions are equal. A docstring that's missing a recently-added parameter is a minor maintenance issue. But a module docstring that describes a fundamentally different responsibility than what the code actually does — that's a design-level concern. It means either the code has drifted from its original purpose without the author recognizing it, or the documentation reflects a misunderstanding of the system's architecture. Either way, future developers will be misled.

Watch for:

- **Purpose contradictions.** A class docstring says "handles user authentication" but the class also manages session storage, rate limiting, and audit logging. The stated purpose and actual responsibilities have diverged.

- **Cross-reference inconsistencies.** A comment in module A says "module B handles validation" but module B's docstring makes no mention of validation, and the validation logic actually lives in module C. The system's documented architecture doesn't match reality.

- **Stale intent.** A PR description says "refactor the payment flow to use the new gateway" but the code still contains branches for the old gateway with no deprecation path. The stated intent and the implementation tell different stories about what this change accomplishes.

When you find these contradictions, surface them. If the contradiction is genuinely conceptual — about purpose, responsibility, or design — it's a high-priority finding. If it's merely a stale parameter list or an outdated code comment, it falls into the lower tiers.

## Design First

Once you understand the intent, evaluate the design before anything else.

Design issues have the highest compounding cost of anything a reviewer can catch. A bug is expensive if it reaches production but is typically bounded — it affects one behavior, and once found, the fix is straightforward. A bad abstraction is different. It becomes the foundation that other code builds on. It shapes how future developers think about the problem. It makes some future changes easy and others unnecessarily hard. The longer it lives, the more code depends on it, and the more expensive it becomes to change.

When reviewing design, you're asking questions like these (among others):

- **Are the abstractions well-chosen?** Does each component have a clear, singular responsibility? Are things grouped by what changes together, or scattered across unrelated concerns? Would someone unfamiliar with the codebase understand why these pieces are organized this way?

- **Is the code at the right level of abstraction?** High-level orchestration should read like a summary — you should be able to understand what happens without reading every implementation detail. Low-level implementation should be contained in focused functions that don't leak their complexity upward. Mixing levels of abstraction in a single function is a design smell.

- **Does this fit the existing architecture?** Every codebase has established patterns — how data flows, how errors propagate, how modules communicate. A PR that introduces a new pattern where an existing one would serve creates cognitive overhead for every future reader. If the new pattern is genuinely better, that's a conversation worth having — but the burden of justification should be on the new pattern, not the old one.

- **Is the public API surface right?** Functions, classes, and modules that are exposed to consumers (whether other teams, other modules, or future code in the same module) form a contract. Contracts are expensive to change. Review whether the exposed surface is minimal, well-named, and unlikely to need breaking changes as the feature evolves.

- **Will this be easy or hard to extend?** Not in a speculative "what if we need X someday" sense — that leads to over-engineering. But in a concrete sense: given the stated direction of this feature or system, does this design leave reasonable room for the next likely steps? Or does it paint into a corner?

- **Are there unnecessary dependencies?** Every dependency is a coupling point. Does this change introduce dependencies that could be avoided? Does it couple things that should be independent?

Design feedback is the most valuable feedback a reviewer can provide because it's the feedback the author is least likely to catch on their own. Authors are deep in the implementation details. They see the trees. The reviewer's comparative advantage is seeing the forest.

## Correctness and Security

After design, turn to correctness. Bugs and security vulnerabilities are urgent — they cause immediate harm if shipped.

For bugs, focus on the logic that's hardest to test and easiest to get wrong: state transitions, boundary conditions, concurrent access, error handling paths that are rarely exercised. Code that looks straightforward on the happy path often harbors subtle issues when inputs are unexpected, resources are unavailable, or operations are interleaved.

For security, focus on trust boundaries. Where does user-controlled input enter the system? Is it validated before use? Are there injection vectors — SQL, command, template? Are secrets handled correctly? Are authorization checks applied consistently? Security issues are particularly valuable to catch in review because they're often invisible to the test suite — the code works correctly for legitimate inputs, and the dangerous behavior only manifests under adversarial use.

Not every function needs a paranoid review for correctness. Focus your attention on code that handles external input, manages state, coordinates concurrent operations, or sits at system boundaries. Internal utility functions that transform data are less likely to harbor critical bugs — and if they do, tests will usually catch them.

## Logic and Edge Cases

After correctness, consider whether the code handles realistic edge conditions. This is distinct from bugs — the code may be technically correct but incomplete. It works on the happy path but fails under conditions that will occur in practice.

The key word is "realistic." Every function has an infinite number of theoretical edge cases. The reviewer's judgment lies in distinguishing between edge cases that will actually happen and those that won't. A function that parses user input should handle empty strings. A function that's only called from one internal callsite with validated data probably doesn't need to defend against every conceivable malformation.

When flagging a logic gap, be specific about the scenario. Vague warnings are not actionable.

## Everything Else

Naming, style, simplification, micro-performance optimizations — these are the lowest tier of review feedback. They are not worthless, but their value is small relative to design and correctness, and they carry real cost.

A reviewer who spends their budget on renaming variables and converting loops to comprehensions has implicitly told the author that the design is fine, the logic is sound, and the biggest problems with this PR are cosmetic. If that's not true, the cosmetic feedback is noise that buries the signal.

The temptation to flag style issues is strong because they're easy to spot and unambiguous. Spotting a naming inconsistency requires no deep understanding of the system. But ease of identification does not correlate with importance.

Reserve this tier for cases that genuinely harm readability — a function named `process` that actually deletes records, a boolean parameter whose polarity is inverted from what the name suggests, a 200-line function that could be three 30-line functions with descriptive names. These are worth flagging because they'll confuse the next reader. A variable named `data` instead of `response` in a 10-line function is not.

## What Not to Flag

Some things that commonly appear in code reviews provide little to no value:

- **Pre-existing issues that this PR doesn't make worse.** If the file already had poor naming conventions and the PR follows the existing convention, that's not this PR's problem. File a separate issue if it matters enough.

- **Style preferences that aren't project conventions.** If the project doesn't have a convention about single-line vs. multi-line conditionals, don't invent one during review. Formatters and linters exist for style enforcement; human review time is too expensive for it.

- **Hypothetical future requirements.** "What if we need to support multiple databases someday?" is not a review comment unless the PR description says they're planning to support multiple databases. Review the code for what it needs to do, not for what it might need to do.

- **Performance concerns without evidence.** Micro-optimizations are rarely worth the review budget unless the code is in a proven hot path. If you're unsure whether it matters, it doesn't.

## Confidence

Not every observation deserves to become a finding. The reviewer should maintain a confidence threshold and drop findings that don't meet it.

False positives are actively harmful. A reviewer who regularly flags non-issues trains recipients to skim review findings rather than engage deeply with them. Each false positive spends budget without providing value and erodes trust for legitimate findings.

Before committing to a finding, ask:

- Have I read enough context to understand why this code exists?
- Am I confident this is actually wrong, or am I uncertain about the language, framework, or business domain?
- Is this something I would flag if I only had three comments to make on this entire PR?

If the answer to any of these is "no," the finding should be dropped or clearly marked as low-confidence.

## The Budget

All of the principles above serve a single idea: review feedback is a scarce resource.

Every finding costs the reader time and attention. A review with 20 findings — most of them about naming or formatting — sends the signal that the reviewer cares more about surface polish than substance. The reader becomes fatigued and may miss the two findings that actually matter.

Contrast this with a review that surfaces 4 findings, all substantive. Each one carries weight because the reviewer has been selective.

The budget is not fixed. A PR that introduces a critical security vulnerability or fundamentally misguided architecture warrants more findings than a PR that's well-designed with a minor logic gap. But even in the worst case, the budget constrains: prioritize the most important findings and be explicit about which ones are critical versus advisory.

The measure of a good code review is not how many issues it finds. It is whether the issues it raises are the ones that matter most.

## Summary

1. **Understand before you evaluate.** Read the PR description, referenced issues, and broader context before reading code. If context is unclear, ask. Proceed only after you have a mental model of the change's intent.
2. **Surface contradictions between intent and implementation.** When documentation, comments, and code tell different stories about purpose or design, that's a high-priority finding.
3. **Evaluate design first.** Abstractions, responsibilities, architectural fit, API surface, extensibility, and coupling have the highest compounding cost. This is where the reviewer's comparative advantage lies.
4. **Then correctness and security.** Bugs and vulnerabilities are urgent. Focus on trust boundaries, state management, concurrency, and error paths.
5. **Then logic gaps.** Code that works on the happy path but fails under realistic edge conditions. Be specific about the scenario.
6. **Everything else is low priority.** Naming, style, simplification, and micro-performance are worth flagging only if the budget allows and the issue genuinely harms readability.
7. **Only flag what this PR introduces.** Pre-existing issues belong elsewhere unless the PR makes them worse.
8. **Maintain high confidence.** False positives erode trust. Drop uncertain findings or mark them as low-confidence.
9. **Treat feedback as a scarce budget.** Fewer, better findings outperform many shallow ones. The quality of a review is measured by the importance of what it raises, not the quantity.
