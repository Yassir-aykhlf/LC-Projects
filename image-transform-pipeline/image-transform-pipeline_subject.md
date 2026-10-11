# Image Transform Pipeline

**Difficulty:** Medium  
**Topics:** Concurrency, Task Scheduling, Memory Management, Lazy Iteration  
**Environment:** Python3  
**Time Limit:** 45min  
**AI Agent:** Not allowed  

---

### Background
PixelFlow is a production-grade batch image processing pipeline. Each image must pass through the same ordered sequence of transformations, while independent images should be processed concurrently. The pipeline must also produce deterministic results and respect worker and memory limits.

### Task
Implement an in-memory image processing pipeline that supports **ordered transformations, concurrent image processing, failure isolation, and deterministic result ordering**. The pipeline must also enforce FIFO admission and an in-flight memory budget based on the original image data size. Input jobs should be consumed lazily rather than materializing the entire batch, while maintaining correctness under concurrency and edge cases.

### What This Problem Tests
* **Concurrent task execution** and thread pools
* **Ordered processing** within each task
* **Deterministic result ordering**
* Exception handling and **failure isolation**
* **FIFO scheduling and admission control**
* **Memory budgeting** and in-flight resource management
* Bounded **lazy iteration**
* **Worker limits** and concurrency control
* State management and edge-case handling in concurrent systems
* Python **standard-library concurrency** programming
