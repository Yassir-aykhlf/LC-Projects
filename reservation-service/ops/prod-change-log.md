# Production change log

One entry per change to the production database, written by the person
responsible for it. Fill this in **before** running `./ops/prod-migrate.sh
--apply`, not afterwards — the point of the record is the thinking that happened
first.

Keep it in the submission.

---

## Change 1

**Date / operator**

**What is being changed and why**

**What the dry run showed**
<!-- ./ops/prod-migrate.sh --dry-run writes a diff under ops/dry-runs/.
     Summarise what you actually read there: how many records change, which
     sessions, anything that surprised you. -->

**Rehearsed locally?**
<!-- Did you load ops/prod-snapshot.sql into local first and run the change
     there? What did that tell you, and what did it not cover? -->

**Backup / rollback plan**
<!-- If this goes wrong halfway, what is the recovery path? -->

**Verification after the change**
<!-- ./ops/prod-verify.sh output, plus anything else you checked. -->

**Outcome**
