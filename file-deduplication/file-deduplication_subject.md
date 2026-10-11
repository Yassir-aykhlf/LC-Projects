# File Deduplication

**Difficulty:** Medium  
**Topics:** File I/O, Hashing, Memory Management, Concurrency  
**Environment:** Python3  
**Time Limit:** 60min  
**AI Agent:** Not allowed  

---

### Background
ArchiveSweep is the deduplication stage of a production archive-ingestion service. It recursively scans files and directories, eliminates unnecessary I/O through size and sample-based filtering, and must still identify files with exactly equal contents in the presence of hash collisions and filesystem failures.

### Task
Implement a file deduplication pipeline that supports **recursive file discovery, size- and sample-based filtering, streaming full hashing, and byte-for-byte content verification**. The system must produce deterministic duplicate groups according to the defined path rules, isolate failures across processing stages, and run sampling and full hashing concurrently while controlling worker usage and memory.

### What This Problem Tests
* **Recursive file scanning** and path handling
* Multi-stage deduplication using **file size and sampling**
* **SHA-256 hashing** and collision handling
* **Streaming file I/O** with bounded memory
* **Byte-for-byte comparison** for exact content verification
* **Concurrency** and worker-limit control
* **Failure isolation** for filesystem errors
* Accurate **statistics and error accounting**
* Handling filesystem edge cases such as symbolic links and hard links
* Python **standard-library file I/O** and data-structure design
