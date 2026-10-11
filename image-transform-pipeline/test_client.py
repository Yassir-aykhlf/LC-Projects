import threading

from image_pipeline import ImageJob, ImagePipeline


def test_transforms_are_applied_in_order():
    pipeline = ImagePipeline(max_workers=2, memory_limit_bytes=100)
    result = pipeline.run([ImageJob("one", b"a")], [lambda b: b + b"b", bytes.upper])
    assert result[0].data == b"AB"


def test_result_order_matches_input_order():
    first_started = threading.Event()
    second_done = threading.Event()
    release_first = threading.Event()

    def controlled(data):
        if data == b"first":
            first_started.set()
            assert second_done.wait(1)
            assert release_first.wait(1)
        else:
            assert first_started.wait(1)
            second_done.set()
        return data

    state = {}
    jobs = [ImageJob("first", b"first"), ImageJob("second", b"second")]
    thread = threading.Thread(
        target=lambda: state.setdefault("result", ImagePipeline(2, 100).run(jobs, [controlled]))
    )
    thread.start()
    assert second_done.wait(1)
    release_first.set()
    thread.join(timeout=2)
    assert not thread.is_alive()
    assert [r.image_id for r in state["result"]] == [
        "first",
        "second",
    ]


def test_constructor_rejects_invalid_limits():
    for workers, memory in [(0, 1), (1, 0)]:
        try:
            ImagePipeline(workers, memory)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid configuration was accepted")
