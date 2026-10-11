# Return Risk Assessment

**Difficulty:** Easy  
**Topics:** AI Coding, Debugging, Input Validation, Boundary Conditions, Batch Processing, Stateless Design, Data Isolation  
**Environment:** Python  
**Time Limit:** 45min  
**AI Agent:** Allowed  

---

### Background
ReturnGuard calculates return risk from customer ratings, purchase value, and account age. The current implementation has issues with input validation, scoring ranges, decision boundaries, and batch processing.

### Task
Repair the risk scoring pipeline to correctly implement **input validation, component scoring, threshold rules, decision mapping, and batch error isolation**. The implementation must distinguish booleans from integers, handle value and account-age boundaries precisely, preserve input order during batch evaluation, and prevent calls or returned data from affecting one another.

### What This Problem Tests
* **Input validation** and type checking
* **Tiered rules** and boundary conditions
* **Deterministic scoring** and rule mapping
* **Batch processing** and error isolation
* **Iterator** single-pass consumption
* **Stateless design** and data isolation
* **Nested data structures** and detached copies
* Python **standard-library data structures** and exception handling
