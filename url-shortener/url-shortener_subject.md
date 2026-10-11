# URL Shortener Service

**Difficulty:** Medium  
**Topics:** Backend, Database, System Design, Full Stack, REST API  
**Time Limit:** 60min  
**AI Agent:** Not allowed  

---

### Background
Build the backend for a URL shortening service that manages mappings between long URLs and short codes. The service must support link creation, redirection, metadata retrieval, deletion, and usage statistics while maintaining data consistency under concurrent requests.

### Task
Implement the core URL shortening service and its HTTP API. The system should support **creating short links, redirecting to original URLs, retrieving link metadata, deleting links, and querying aggregate statistics**. It must handle custom and automatically generated short codes, expiration through TTL, hit counting, ownership validation, and database operations. All responses must follow the defined HTTP status codes and JSON contracts, with database updates protected against concurrent access.

### What This Problem Tests
* **HTTP API and RESTful routing** with Flask
* **SQL / SQLite CRUD** operations
* URL and custom short-code **validation**
* Short-code generation, uniqueness checks, and collision handling
* **TTL and expiration** logic
* Hit counting and aggregate statistics
* Ownership-based **authorization**
* Safe **read-modify-write** operations under concurrency
* Basic **locking and thread safety**
* HTTP status codes, error handling, and strict **JSON response contracts**
* End-to-end **backend engineering** across the API, service, and database layers
