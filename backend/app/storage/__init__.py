"""Storage package for BGSTM artifact binaries (BGSTM#298).

Public API
----------
``get_storage()``
    Returns a :class:`~app.storage.base.StorageBackend` instance configured
    from the current application settings.  This is a **function**, not a
    module-level singleton, so tests can swap :attr:`app.config.settings`
    without import-time side effects.

Backend selection
-----------------
Driven by ``BGSTM_STORAGE_BACKEND`` (``"local"`` or ``"s3"``).
"""

from __future__ import annotations

from app.config import settings
from app.storage.base import StorageBackend, StorageResult
from app.storage.local import LocalFsBackend
from app.storage.s3 import S3Backend

__all__ = [
    "StorageBackend",
    "StorageResult",
    "LocalFsBackend",
    "S3Backend",
    "get_storage",
]


def get_storage() -> StorageBackend:
    """Return a :class:`StorageBackend` based on the current settings.

    Called fresh on each request so tests can swap settings safely.
    """
    backend = settings.BGSTM_STORAGE_BACKEND.lower()
    if backend == "local":
        return LocalFsBackend(
            root=settings.BGSTM_ARTIFACTS_DIR,
            url_prefix=settings.BGSTM_ARTIFACT_URL_PREFIX,
        )
    if backend == "s3":
        return S3Backend()
    raise ValueError(f"Unknown BGSTM_STORAGE_BACKEND={backend!r}; expected 'local' or 's3'.")
