
# PixelFlow: Concurrent Image Transformations

Estimated implementation time: 45 minutes.

## Scenario

PixelFlow is the execution core of a production batch-image service. Every
image goes through the same ordered transform chain. Independent images should
run concurrently, while the service must remain deterministic and stay within
its worker and admission-memory limits.

The repository provides the stable public data model, constructor validation,
and method signatures. Implement the production pipeline in `image_pipeline.py`.

## What to build

Implement `image_pipeline.py` from the provided scaffold. Keep the following public names and signatures::

    Transform = Callable[[bytes], bytes]
    ImageJob(image_id: str, data: bytes)
    TransformResult(`index`, `image_id`, `data`, error)
    ImagePipeline(max_workers=4, memory_limit_bytes=16_000_000)
    ImagePipeline.run(jobs, transforms) -> list[TransformResult]

Only the Python standard library may be used.

## Required behavior

### Ordered per-image processing

- Apply every transform exactly once, in the supplied order.
- The output bytes from one transform become the input to the next.
- An empty transform chain is an identity operation.

### Deterministic results

- Return exactly one result for every consumed input.
- Results are always in input order, regardless of completion order.
- `index` is the zero-based input position.
- `image_id` is copied unchanged from that input. Duplicate IDs are allowed.

### Failure isolation

If a transform raises `Exception`:

- stop processing that image immediately; do not call later transforms for it;
- return data=None;
- return error="ExceptionType: message", preserving empty or multiline messages;
- continue processing all other images.

Do not catch `BaseException`.

### Worker limit

No more than `max_workers` image chains may run at the same time. If at least
`max_workers` eligible jobs are blocked inside their transforms, the pipeline
must be able to start `max_workers` chains. A serial executor does not meet this
requirement.

## Extended behavior

### FIFO admission

Admit jobs in input order. If the job at the head of the input is too large to
admit, do not skip it to run a smaller job that appears later.

### In-flight byte budget

`memory_limit_bytes` is the admission budget for the original `ImageJob.data`
bytes of every submitted or in-flight job, including queued futures. Keep a
job's input bytes charged against the budget until its full transform chain
succeeds or fails.

- Do not submit a job when doing so would exceed the budget.
- A single oversized head job must still progress, but only while no other job
  is in flight.
- Transform outputs, decoded buffers, and executor overhead are not included in this exercise’s byte budget.

### Bounded iterable consumption

`jobs` may be a one-pass iterable. Read it lazily. At any point, you may have
requested the admitted jobs plus one pending head item, but you must not
materialize the complete input.

At most `max_workers` jobs may be submitted or in flight at once, including
executor queue entries. While every submitted chain is blocked, at most
`max_workers + 1` inputs may have been requested.

Constructor arguments must remain positive. Empty batches are valid.

## Bonus discussion

After implementing the pipeline, answer the questions in `REFLECTION.essay`. They ask
about scheduler trade-offs, distributing a batch of one million images, and the memory metrics you would measure in production. These answers are discussion material;
hidden tests do not grade additional behavior from them.

## Example

Suppose the input contains three jobs:

- index 0: `ImageJob(image_id="a", data=b"x")`
- index 1: `ImageJob(image_id="b", data=b"y")`
- index 2: `ImageJob(image_id="a", data=b"z")`

The transform chain first appends `b"!"` and then runs a transform that
uppercases its input, except that it raises `ValueError("invalid image")` for
`b"y!"`. A valid result is:

    TransformResult(index=0, image_id="a", data=b"X!", error=None)
    TransformResult(
        index=1,
        image_id="b",
        data=None,
        error="ValueError: invalid image",
    )
    TransformResult(index=2, image_id="a", data=b"Z!", error=None)

The returned list remains in input order even if index 2 finishes before
index 0. Duplicate `image_id` values are preserved and do not affect ordering.
A failure in one image does not prevent the remaining images from completing.

## Running the visible tests

    python3 -m pytest -q -p no:cacheprovider test_client.py

Do not modify `README.md`, `README_CN.md`, or `test_client.py`. Add regression tests where appropriate.
