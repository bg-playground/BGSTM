"""Local filesystem storage backend for artifact uploads (BGSTM#298).

Used as the default backend for development and tests.  Files are stored under
``settings.STORAGE_LOCAL_ROOT`` and served via a static-files mount at
``settings.STORAGE_LOCAL_PUBLIC_BASE_URL``.
"""

import asyncio
import re
from pathlib import Path
from typing import BinaryIO

from app.storage.base import StorageBackend

_UNSAFE_RE = re.compile(r"[^\w.\-]")
_CHUNK_SIZE = 65_536  # 64 KB per read


def _make_safe(name: str) -> str:
    """Replace non-alphanumeric/dot/dash characters with underscores."""
    return _UNSAFE_RE.sub("_", name) or "file"


class LocalFsBackend(StorageBackend):
    """Stores artifacts on the local filesystem.

    Args:
        root: Directory under which all artifacts are stored.
        public_base_url: Base URL at which ``root`` is served (e.g. via a
            ``StaticFiles`` mount).  Must NOT end with a slash.
    """

    def __init__(self, root: Path, public_base_url: str) -> None:
        self.root = root
        self.public_base_url = public_base_url.rstrip("/")
        self.root.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, body: BinaryIO, content_type: str) -> str:  # noqa: ARG002
        """Write *body* to ``root/key`` and return its public URL."""
        dest = self.root / key

        def _write() -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as fh:
                while True:
                    chunk = body.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    fh.write(chunk)

        await asyncio.to_thread(_write)
        return await self.url_for(key)

    async def url_for(self, key: str, expires_in: int = 3600) -> str:  # noqa: ARG002
        """Return the permanent public URL for *key*."""
        return f"{self.public_base_url}/{key}"

    async def delete(self, key: str) -> None:
        """Remove the file at ``root/key`` if it exists."""
        dest = self.root / key

        def _remove() -> None:
            dest.unlink(missing_ok=True)

        await asyncio.to_thread(_remove)
