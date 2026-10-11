# Retry-Safe Issue Service

**Difficulty:** Hard  
**Topics:** API Design, Idempotency, Concurrency, Authorization, Versioning, Pagination  
**Environment:** Python  
**Time Limit:** 75min  
**AI Agent:** Not allowed  

---

### Background
IssueHub is a project issue management service. It must remain consistent when clients retry creation requests and team members concurrently update issues, while keeping data and access isolated across projects.

### Task
Implement an issue service supporting **issue creation, retrieval, status transitions, and paginated listing**. The service must enforce authorization and input validation, safely handle duplicate creation requests through idempotency keys, and use version checks to coordinate concurrent updates. Expose the service through the provided HTTP adapter while preserving atomicity for failed operations and isolation of inputs and returned data.

### What This Problem Tests
* **Authorization** and access control
* **Idempotency** and retry safety
* **Concurrency control** and race-condition handling
* **Optimistic locking / version control**
* **Atomic operations** and state consistency
* **Pagination** and cursor-based queries
* **HTTP APIs** and request handling
* Input validation and **error handling**
* Snapshot and **state isolation**
* In-memory data modeling and data-structure design
