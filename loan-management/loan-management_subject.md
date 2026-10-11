# Loan Lifecycle & Balance Management

**Difficulty:** Medium  
**Topics:** AI Coding, Debugging, Concurrency, State Management, Data Modeling  
**Environment:** Python  
**Time Limit:** 60min  
**AI Agent:** Allowed  

---

### Background
LedgerBridge is an in-memory loan service with bugs affecting loan retrieval, funding balances, and repayments. Repair the core business logic while preserving the existing public API and maintaining data consistency under concurrent requests.

### Task
Repair the loan service to support **loan creation and retrieval, funding, repayment, balance management, and concurrency safety**. The service must validate amounts and users, enforce loan state transitions from `pending` to `active` to `repaid`, maintain balance conservation during transfers, and prevent concurrent operations from corrupting loan or balance state. Returned data must also remain isolated from the service's internal state.

### What This Problem Tests
* **In-memory data modeling** and loan lifecycle management
* **State transitions** and business-rule validation
* **Balance transfers** and conservation
* Input validation and **error handling**
* **Concurrency control** and thread safety
* **Atomic state updates** under concurrent funding
* **Consistency** when operations fail
* **Snapshot isolation** for returned data
* State persistence and **instance isolation**
* Python **standard library** and service design fundamentals
