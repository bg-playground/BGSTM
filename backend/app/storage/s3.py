"""S3 storage backend stub (BGSTM#298).

Real implementation is out of scope for this milestone; set
``BGSTM_STORAGE_BACKEND=local`` to use the local filesystem backend.
"""

from __future__ import annotations

from .base import StorageBackend, StorageResult


class S3Backend(StorageBackend):
    """Stub S3 backend — raises :class:`NotImplementedError` on every call.

    Set ``BGSTM_STORAGE_BACKEND=local`` to use the local filesystem backend.
    """

    def save(self, stream, *, key: str, content_type: str) -> StorageResult:
        raise NotImplementedError("S3 backend not yet implemented; set BGSTM_STORAGE_BACKEND=local")

    def url_for(self, key: str) -> str:
        raise NotImplementedError("S3 backend not yet implemented; set BGSTM_STORAGE_BACKEND=local")
