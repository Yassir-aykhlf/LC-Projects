# Keyword and User Blocking

**Difficulty:** Medium  
**Topics:** Input Validation, State Management, Concurrency  
**Environment:** Python  
**Time Limit:** 60min  
**AI Agent:** Not allowed  

---

### Background
ContentGate is a request admission component for a discussion service. It determines whether requests are allowed based on configurable keywords and user block status, while automatically blocking users after repeated violations.

### Task
Implement the complete content admission service with **configuration validation, keyword normalization and matching, user blocking, strike tracking, and concurrency safety**. The service must support both manual and violation-based blocking, apply configuration updates atomically, and isolate instance state from returned results.

### What This Problem Tests
* **Input validation** and exception handling
* **String normalization** and case-insensitive matching
* **Sets** and deduplication
* **String searching** and substring matching
* **State management** and state transitions
* **Counters** and accumulated state
* **Concurrency control** and thread safety
* **Atomic operations** and state consistency
* **Data copying** and state isolation
* **Iterators / Iterables** and one-pass input handling
