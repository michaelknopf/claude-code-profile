# Smoke Test Principles

Smoke tests occupy a distinct role in the testing pyramid. Unlike unit tests, which verify isolated components through mocked dependencies, smoke tests validate that a system functions correctly in a realistic environment with actual infrastructure. This distinction is fundamental to understanding how to design them well.

## The Core Principle: Less is More

Smoke tests are inherently slow and brittle. They interact with real databases, queues, external APIs, and other infrastructure—components that introduce latency, network variability, and state that persists between runs. Because of these characteristics, every smoke test carries a maintenance burden that unit tests do not.

The temptation when writing smoke tests is to be thorough—to cover edge cases, validate error handling, and test every code path. Resist this temptation. Comprehensive coverage is the domain of unit tests. Smoke tests should be few in number, each one carefully justified, and designed to validate what cannot be tested any other way.

## What Smoke Tests Are For

Smoke tests serve two purposes that unit tests cannot:

**1. Validating Integration Points**

When code depends on external components—databases, message queues, third-party APIs, file systems—unit tests mock these dependencies. Mocks verify that your code *would* behave correctly *if* the external component behaved as expected. Smoke tests verify that the actual integration works: that connection strings are correct, authentication is configured properly, serialization is compatible, and the contract between systems holds.

**Example: Database Queries**

Consider a complex SQL query with joins, aggregations, or database-specific functions. In a unit test, you might mock the database client and verify that the correct query string is constructed—but this tells you nothing about whether the query actually works. The mock cannot validate SQL syntax, verify that referenced tables and columns exist, confirm that indexes are used efficiently, or catch subtle differences between database engines.

Smoke tests execute real queries against real databases. They validate that:

- The query syntax is valid for the target database engine
- All referenced tables, columns, and relationships exist
- The query returns expected results for known test data
- Database permissions are correctly configured
- Connection pooling and timeout settings work under realistic conditions

This same principle applies to other infrastructure interactions: Elasticsearch queries, Redis commands, S3 operations, or any system where the behavior depends on the actual implementation rather than an interface contract. Unit tests verify your code's logic; smoke tests verify that your code's assumptions about external systems are correct.

**2. Guarding Against Misconfiguration**

Infrastructure can be provisioned incorrectly. Environment variables can be missing or wrong. Feature flags can be in unexpected states. These are failure modes that exist only in deployed environments and cannot be caught by unit tests running against mocked dependencies. Smoke tests catch these issues before they affect users.

## Deployment Contexts

Smoke tests run in two distinct settings, each with different constraints and purposes:

**1. Isolated Test Deployments**

CI/CD pipelines—both for pull requests and post-merge—spin up ephemeral, isolated deployments of the service. These environments exist solely for testing: to verify that the service deploys successfully and passes sanity checks before code is merged or promoted.

In isolated deployments, smoke tests have more freedom. The environment is not shared with real traffic or other systems. Tests can consume from queues, write to databases, and interact with infrastructure without risk of interfering with production workloads.

**2. Live Environments**

After deployment to staging, production, or other shared environments, smoke tests verify that the new deployment is functioning correctly in its actual operating context. These tests validate that configuration is correct, infrastructure is properly provisioned, and the service integrates with its real dependencies.

In live environments, smoke tests must be more constrained. They share the environment with real traffic and cannot take actions that would interfere with normal operations.

**Conditional Test Execution**

Because of these differences, some tests should only run in isolated deployments. A test that validates queue-to-queue processing, for instance, might consume from an output queue in an isolated environment—but doing so in production would steal messages from the real consumer.

Design your test suite with this distinction in mind. Tests that serve primarily as integration validation—verifying that components work together—may be appropriate only for isolated deployments. Tests that verify environment configuration and deployment health should run in both contexts.

## Designing Effective Smoke Tests

### Test Complete Flows, Not Fragments

A well-designed smoke test validates an entire lifecycle or user journey. Consider a resource management API. Rather than writing separate tests for create, read, update, and delete operations, write a single test that exercises the complete CRUD cycle:

1. Create the resource
2. Retrieve it to verify creation succeeded
3. Update the resource
4. Retrieve it again to verify the update took effect
5. Delete the resource
6. Attempt retrieval to confirm deletion (expect a 404)

This approach validates that all operations work together correctly, that state transitions behave as expected, and that the system is properly configured—all in a single test.

**The Cost of Fragmentation**

Contrast this with the alternative: separate smoke tests for each operation. A test for "update" must first create a resource to update. A test for "delete" must first create a resource to delete. A test for "get" must first create a resource to retrieve. Each test duplicates setup work, and each must handle its own cleanup.

The arithmetic is unfavorable. If the unified test makes 6 API calls, four separate tests might make 16 or more—each requiring create, act, verify, and cleanup steps. This multiplication has consequences:

- **Longer test runs.** More API calls mean more time, especially when each call involves network latency and database operations.
- **More opportunities for transient failures.** Each API call is a chance for a timeout, connection reset, or temporary unavailability. Doubling the calls roughly doubles the flakiness.
- **Slower recovery from failures.** When a flaky test fails, it must be retried. A test suite that takes twice as long takes twice as long to retry.

The unified flow is not just more elegant—it is more reliable.

### Asynchronous Processing Flows

Many services process work asynchronously. A request arrives via an API or queue, processing happens in the background, and results become available later. Smoke tests must accommodate this pattern.

**Example: API-Triggered Async Processing**

Consider a service that accepts requests via API, processes them asynchronously, and stores results that can be retrieved later:

1. Submit a request to the API
2. Poll a status or results endpoint until processing completes
3. Verify the results match expectations
4. Clean up the created resources

The key is polling rather than sleeping. A fixed sleep duration is either too short (causing flakiness) or too long (wasting time). Poll with a reasonable interval and timeout.

**Example: Queue-to-Queue Processing (Isolated Deployments Only)**

Some services consume from an input queue, perform processing, and publish results to an output queue. In isolated test deployments, you can validate this flow directly:

1. Begin listening to the output queue
2. Publish a test message to the input queue
3. Wait for the corresponding message to appear on the output queue
4. Verify the output message contents

This test validates the complete processing pipeline but can only run in isolated deployments. In a live environment, consuming from the output queue would intercept messages intended for downstream services. For live environments, consider alternative approaches: an API that exposes processing status, logs, or metrics that confirm processing occurred, or simply omitting this test from the live suite.

### Use External-Facing Interfaces

Smoke tests should interact with the system through the same interfaces that real consumers use: public APIs, message queues, or other integration points. Avoid reaching into internal implementation details.

When a smoke test requires additional control—to force a specific behavior or to verify internal state—consider whether the system itself should expose that capability. A well-designed system often benefits from observability endpoints, administrative APIs, or configuration options that serve both operational needs and testability. Prefer enhancing the system over adding test-only backdoors.

When test-specific hooks are unavoidable, implement them thoughtfully. Consider security implications. Ensure they cannot be exploited in production. Document their existence and purpose.

### Design for Determinism

Flaky tests erode trust. A test that sometimes passes and sometimes fails—without any actual change to the system—becomes noise rather than signal.

Design smoke tests to produce deterministic results:

- **Avoid timing dependencies.** If a test depends on asynchronous processing, poll for completion rather than sleeping for a fixed duration.
- **Isolate test data.** Use unique identifiers for resources created by tests so they do not collide with each other or with real data.
- **Control the environment.** When possible, configure the system to behave predictably during tests.

### Be Defensive About Cleanup

Smoke tests run in shared environments. A test that fails mid-execution may leave behind resources that interfere with subsequent runs. Therefore, smoke tests must clean up not only after themselves but also *before* they run.

At the start of each test, assume that a previous execution may have failed to clean up. Proactively remove any resources that the test will create. This defensive approach ensures that tests are idempotent and can be run repeatedly without manual intervention.

## Being a Good Citizen

Smoke tests share their environment with other systems and processes. They must not pollute shared resources or distort operational metrics.

**Identifiable Test Data**

When a smoke test creates data, that data must be clearly identifiable as test data. Use naming conventions, tags, or dedicated fields that allow other systems to filter out test artifacts. This prevents test data from contaminating analytics, reports, or downstream processing.

**Observable as Tests**

Include headers, trace IDs, or other markers that identify traffic as originating from smoke tests. This allows observability systems to distinguish test traffic from real traffic, preventing tests from inflating metrics or triggering false alerts.

**Minimal Footprint**

Create only the resources necessary for the test. Clean up completely when done. Avoid leaving orphaned data that accumulates over time and becomes difficult to manage.

## Summary

Effective smoke testing requires restraint. Each smoke test should:

- Validate integration points or configuration that cannot be tested in isolation
- Cover a complete flow or lifecycle rather than individual operations
- Use the system's external interfaces rather than implementation details
- Be deterministic and resilient to environmental variability
- Clean up defensively, both before and after execution
- Identify itself clearly to avoid polluting shared resources and metrics

The measure of a good smoke test suite is not comprehensiveness but precision: few tests, each indispensable, each covering broadly but shallowly. Depth of coverage belongs to unit tests. Smoke tests exist to verify that the pieces fit together correctly in the real world.
