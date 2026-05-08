"""Storage backend ABC and shared types (BGSTM#298)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StorageResult:
    """Returned by :meth:`StorageBackend.save` after a successful write."""

    key: str
    url: str
    size_bytes: int
    content_type: str


class StorageBackend(ABC):
    """Pluggable storage abstraction for artifact binaries."""

    @abstractmethod
    def save(self, stream, *, key: str, content_type: str) -> StorageResult:
        """Persist *stream* under *key* and return a :class:`StorageResult`.

        ``stream`` must be a file-like object opened in binary mode,
        seeked to the beginning.  The implementation is responsible for
        reading and closing/discarding the stream.
        """

    @abstractmethod
    def url_for(self, key: str) -> str:
        """Return the public download URL for *key*."""
