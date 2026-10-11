# Password Reset

**Difficulty:** Easy  
**Topics:** AI Coding, Debugging, Configuration Management, Datetime Handling, State Management, Data Persistence  
**Environment:** Python  
**Time Limit:** 45min  
**AI Agent:** Allowed  

---

### Background
The Password Reset Service manages the password recovery workflow. The current implementation incorrectly rewrites the authentication URL, calculates reset-code expiration incorrectly, fails to persist some password changes, and allows previously used reset codes to be replayed.

### Task
Repair the password reset workflow to correctly handle **configuration loading, reset-code lifecycle, timezone-aware time calculations, password state updates, and one-time code consumption**. The service must enforce the exact 30-second validity window, support both timezone-aware and legacy naive timestamps, persist password and reset state through the provided database boundary, and keep users and service instances properly isolated.

### What This Problem Tests
* **Environment variable configuration** and configuration snapshots
* **Random value generation** and uniqueness guarantees
* **Datetime handling** and timezone conversion
* **Time windows** and boundary conditions
* **State persistence** through a storage API
* **State lifecycle** and one-time token consumption
* **User data isolation** and state consistency
* **Error handling** and failure paths
* **Data encapsulation** and respecting storage boundaries
* Python **standard-library** datetime, environment-variable, and data-handling APIs
