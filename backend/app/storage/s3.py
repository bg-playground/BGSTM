"""S3 storage backend stub (BGSTM#298).

Importable so that ``settings.STORAGE_BACKEND = 's3'`` fails fast with a clear
error message.  A real implementation is tracked in a follow-up issue.
"""

from typing import BinaryIO

from app.storage.base import StorageBackend


class S3Backend(StorageBackend):
    """Placeholder S3 backend — raises ``NotImplementedError`` on construction."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("S3Backend is not yet implemented. Use STORAGE_BACKEND='local' for now.")

    async def put(self, key: str, body: BinaryIO, content_type: str) -> str:  # pragma: no cover
        raise NotImplementedError

    async def url_for(self, key: str, expires_in: int = 3600) -> str:  # pragma: no cover
        raise NotImplementedError

    async def delete(self, key: str) -> None:  # pragma: no cover
        raise NotImplementedError
