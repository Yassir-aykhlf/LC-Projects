# Comment Moderation

**Difficulty:** Medium  
**Topics:** AI Coding, Debugging, Input Validation, State Management, Concurrency  
**Environment:** Python  
**Time Limit:** 60min  
**AI Agent:** Allowed  

---

### Background
ReviewDesk is a comment service backed by an injected content checker. The system must moderate comments on creation and edit, maintain users' violation state, and remain consistent under concurrent requests and checker failures.

### Task
Implement an in-memory comment service supporting **comment creation, editing and retrieval, content moderation, user-state tracking, and concurrency safety**. The service must enforce validation, ownership, and moderation order, persist strike state across writes, block users after the required threshold, and leave reviews, strikes, and ID allocation unchanged when the checker fails.

### What This Problem Tests
* **Input validation** and operation ordering
* **State management** and state transitions
* **Resource ownership** and authorization checks
* **Exception handling** and failure isolation
* **Concurrency control** and thread safety
* **Atomic state updates** and data consistency
* **ID allocation** and persistent in-memory state
* **Snapshot / deep-copy isolation**
* In-memory data modeling and **CRUD** operations
