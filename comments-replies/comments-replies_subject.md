# Comments & Replies

**Difficulty:** Easy  
**Topics:** Backend, Database, System Design, Full Stack, REST API  
**Time Limit:** 45min  
**AI Agent:** Not allowed  

---

### Background
Build an in-memory comment and reply service for a discussion platform. Users should be able to comment on posts and reply to existing comments, with discussions limited to two levels: **Post → Comment → Reply**. The service must maintain isolated state and remain safe under concurrent requests.

### Task
Implement a comment service that supports **adding comments, adding replies, and retrieving complete comment threads**. The service must validate inputs and resource relationships, maintain independent auto-incrementing IDs for comments and replies, preserve creation order, and prevent callers from modifying internal state through returned data. All operations must remain correct under concurrent access.

### What This Problem Tests
* **In-memory data modeling** and parent-child relationships
* Designing a two-level **comment/reply data structure**
* **Input validation**, resource validation, and error handling
* Maintaining **state isolation** across posts
* Generating unique IDs safely under concurrency
* Basic **locking and thread safety**
* **Snapshot / mutation safety** when returning stored data
* Preserving creation order independently of timestamps
* Choosing appropriate data structures and maintaining reasonable **time complexity**
