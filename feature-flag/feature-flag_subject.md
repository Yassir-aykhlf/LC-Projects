# Feature flag

**Difficulty:** Medium  
**Topics:** Hashing, Locking, Deterministic Assignment, Concurrency, HTTP API  
**Environment:** Python 3  
**Time Limit:** 60min  
**AI Agent:** Not allowed  

---

### Background
Build a feature flag and experiment assignment service for product teams to gradually roll out features and run A/B experiments. Each flag defines a set of variants, ordered targeting rules based on user attributes, and a deterministic percentage rollout for users who do not match any rule.

### Task
Implement an in-memory feature flag service that supports **creating, reading, updating, deleting, listing, and evaluating flags**. The service must validate and normalize configurations, evaluate targeting rules in order, apply deterministic percentage-based bucketing, and return results that are safe for callers to modify. It must also maintain consistent configuration and correct behavior under concurrent requests.

### What This Problem Tests
* **Feature flag and experiment** data modeling
* Configuration validation and normalization
* **Ordered rule evaluation** with first-match-wins and AND conditions
* Handling user attributes and multiple **targeting operators**
* **Deterministic hashing and percentage-based bucketing**
* Maintaining stable user assignments as rollout percentages change
* **Concurrency, locking, and configuration consistency**
* Safe handling of shared in-memory state and mutable return values
* Preserving **API contracts** and clean error handling
* Reasoning about deterministic assignment and configuration sharing in **multi-instance systems**
