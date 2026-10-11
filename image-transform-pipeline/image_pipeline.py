"""Starter scaffold for the PixelFlow production pipeline.

The stable public data model and constructor are provided. Implement the
per-image execution path and bounded concurrent scheduler described in README.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

Transform = Callable[[bytes], bytes]


@dataclass(frozen=True)
class ImageJob:
    image_id: str
    data: bytes


@dataclass(frozen=True)
class TransformResult:
    index: int
    image_id: str
    data: bytes | None
    error: str | None


class ImagePipeline:
    def __init__(self, max_workers: int = 4, memory_limit_bytes: int = 16_000_000):
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        if memory_limit_bytes < 1:
            raise ValueError("memory_limit_bytes must be positive")

        # Maximum number of image jobs that may execute concurrently.
        self.max_workers = max_workers

        # Maximum admitted input bytes allowed at the same time.
        self.memory_limit_bytes = memory_limit_bytes

    @staticmethod
    def _run_one(
        index: int,
        job: ImageJob,
        transforms: Sequence[Transform],
    ) -> TransformResult:
        """Apply all transforms to one image and return its result."""
        raise NotImplementedError

    def run(
        self,
        jobs: Iterable[ImageJob],
        transforms: Sequence[Transform],
    ) -> list[TransformResult]:
        """Process all jobs according to the ordering, concurrency, and memory contract."""
        raise NotImplementedError