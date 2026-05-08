"""Local filesystem storage backend (BGSTM#298).

Writes artifacts under a configurable root directory and returns URLs
served by the dev-only static-files route mounted in ``main.py``.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .base import StorageBackend, StorageResult


class LocalFsBackend(StorageBackend):
    """Stores artifacts on the local filesystem.

    Args:
        root: Directory under which all artifact files are written.
            Created on demand if it does not exist.
        url_prefix: Base URL prefix used to construct download URLs.
            E.g. ``http://localhost:8000/artifacts``.
    """

    def __init__(self, root: str | Path, url_prefix: str) -> None:
        self._root = Path(root)
        self._url_prefix = url_prefix.rstrip("/")

    def save(self, stream, *, key: str, content_type: str) -> StorageResult:
        dest = (self._root / key).resolve()
        # Second line of defense: reject keys that escape the artifact root.
        if not dest.is_relative_to(self._root.resolve()):
            raise ValueError(f"storage key {key!r} escapes artifact root")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fp:
            shutil.copyfileobj(stream, fp)
        size_bytes = dest.stat().st_size
        return StorageResult(
            key=key,
            url=self.url_for(key),
            size_bytes=size_bytes,
            content_type=content_type,
        )

    def url_for(self, key: str) -> str:
        return f"{self._url_prefix}/{key}"

    @property
    def root(self) -> Path:
        return self._root

    def delete(self, key: str) -> None:
        """Remove an artifact file.  No-op if it does not exist."""
        target = self._root / key
        try:
            os.unlink(target)
        except FileNotFoundError:
            pass
