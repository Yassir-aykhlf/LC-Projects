# Persistent Private Watchlists

**Difficulty:** Medium  
**Topics:** AI Coding, Debugging, Transactions, Data Persistence, Authorization, Concurrency, Database, CRUD  
**Environment:** Python  
**Time Limit:** 60min  
**AI Agent:** Allowed  

---

### Background
ScreenShelf is a SQLite-backed watchlist management service. The current implementation has incorrect statuses for duplicate movie additions, removes movies from the wrong watchlists, and loses committed changes after reconnecting.

### Task
Repair the watchlist service to support **ownership checks, persistent storage, movie membership management, duplicate-operation handling, and safe deletion**. The service must correctly implement creating, retrieving, renaming, and deleting watchlists, as well as adding and removing movies. All writes must be committed before returning so that separate service instances can observe the same persisted state.

### What This Problem Tests
* **SQLite database operations** and persistence
* **CRUD** operations and resource lifecycle management
* **Entity relationships** and uniqueness constraints
* **Authorization** and resource ownership checks
* **Input validation** and error handling
* **Transactions and commits** for data consistency
* **Database connection management** and resource cleanup
* **Concurrent access** and operation serialization
* **Data isolation** and detached snapshots
* HTTP **REST APIs** and status-code handling
