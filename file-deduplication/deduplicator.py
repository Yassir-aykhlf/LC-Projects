"""Starter scaffold for the ArchiveSweep production deduplication pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DuplicateGroup:
    canonical: str
    duplicates: tuple[str, ...]
    size: int


@dataclass(frozen=True)
class FileIssue:
    path: str
    error: str


@dataclass(frozen=True)
class ScanReport:
    groups: tuple[DuplicateGroup, ...]
    issues: tuple[FileIssue, ...]
    files_considered: int
    bytes_hashed: int


class FileDeduplicator:
    def __init__(self, max_workers: int = 4, sample_size: int = 4096):
        if max_workers < 1 or sample_size < 1:
            raise ValueError("limits must be positive")
        self.max_workers = max_workers
        self.sample_size = sample_size

    def _full_digest(self, path: Path) -> tuple[str, int]:
        """Return the file's full-content fingerprint and bytes read."""
        raise NotImplementedError

    def _sample_fingerprint(self, path: Path, size: int) -> tuple[str, int]:
        """Return a sample-based fingerprint and bytes read for a file."""
        raise NotImplementedError

    def scan(self, paths: Iterable[str | Path]) -> ScanReport:
        """Scan the supplied roots and return all duplicate groups and issues."""
        raise NotImplementedError