# Reservation Service Incident

**Difficulty:** Medium  
**Topics:** AI Coding, Debugging, Concurrency, Database  
**Environment:** Python 3, PostgreSQL 15  
**Time Limit:** 60min  
**AI Agent:** Allowed  

---

### Background
SlotWise is an online course and event reservation service where users can browse upcoming sessions and remaining capacity, reserve or cancel a place, and view their reservations on the Dashboard. The backend is built with Python (FastAPI + SQLAlchemy + Alembic) and PostgreSQL.

You have just taken over this live service from its previous maintainer, Robin. He has moved to another team and can only answer questions about product behavior in the handover Q&A channel — he cannot debug the system for you or tell you where the defects are.

### Incident
Recent customer support reports indicate that the reservation experience is no longer reliable: the result shown after making a reservation does not match expectations, different parts of the product report conflicting remaining capacity for the same session, and cancellations can leave inconsistent states across the product. The handover contains no trusted diagnosis, only a small test suite and a few sanitized support cases and logs.

### Task
Investigate the application, identify the root causes, fix the defects, and add valuable regression tests. The scope is limited to the backend and persistence layer.

In addition, the production database already contains historical records that are inconsistent with what the product displays. It contains real data and has no reset path, so you must repair the data in place and verify the result.

This is an **AI Coding task**: you will work in a real workspace together with your coding agent to complete the investigation and fixes. How you break down the problem, provide context to the agent, decide how much permission to give it, and determine the pace of verification are all part of the assessment.

### What This Problem Tests
* Collaborating with an **AI agent**: task decomposition, context sharing, permission management, and verification cadence
* **Debugging and root-cause analysis** without an existing diagnosis
* Backend and database correctness under **concurrency and transactions**
* Fixing and refactoring code without breaking **external contracts**
* Handling **production environments** carefully: rehearse first, apply changes safely, and leave verification and records
* Asking questions to fill in **undocumented requirements** and documenting the reasoning behind your decisions
