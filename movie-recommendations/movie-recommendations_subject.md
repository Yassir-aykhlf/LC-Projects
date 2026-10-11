# Personalized Movie Recommendation

**Difficulty:** Medium  
**Topics:** AI Coding, Debugging, Recommender Systems, Sorting, Data Processing, Input Validation  
**Environment:** Python  
**Time Limit:** 60min  
**AI Agent:** Allowed  

---

### Background
NextFrame is a movie recommendation service that uses user ratings and watch history to generate personalized recommendations. The current implementation can return empty or incorrectly ranked results and needs to be repaired while preserving the existing service and HTTP contract.

### Task
Implement the complete recommendation pipeline with **input validation, candidate filtering, genre preference scoring, deterministic ranking, and result limiting**. The system must correctly exclude rated, watched, and unavailable movies, support cold-start users without preference data, and keep source inputs and returned results isolated from each other.

### What This Problem Tests
* **Input validation** and boundary conditions
* **Data filtering** and candidate-set construction
* **Dictionaries and sets** for data modeling and lookup
* **Aggregation** and weighted scoring
* **Sorting** and multi-level tie-breaking
* **Time complexity** and data-structure design
* **Data copying** and state isolation
* **HTTP API** and error handling
* **Edge cases** and empty-input handling
* Python **standard library** and basic service design
