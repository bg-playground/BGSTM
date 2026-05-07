"""Storage package — exports the backend dependency for FastAPI injection."""

from app.config import settings
from app.storage.base import StorageBackend
from app.storage.local import LocalFsBackend

__all__ = ["StorageBackend", "get_storage_backend"]

_backend_instance: StorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """FastAPI dependency that returns the configured storage backend singleton.

    The backend is selected based on ``settings.STORAGE_BACKEND``:

    * ``"local"`` → :class:`~app.storage.local.LocalFsBackend`
    * ``"s3"``    → :class:`~app.storage.s3.S3Backend` (raises ``NotImplementedError`` on init)
    """
    global _backend_instance
    if _backend_instance is None:
        if settings.STORAGE_BACKEND == "local":
            _backend_instance = LocalFsBackend(
                root=settings.STORAGE_LOCAL_ROOT,
                public_base_url=settings.STORAGE_LOCAL_PUBLIC_BASE_URL,
            )
        else:
            from app.storage.s3 import S3Backend

            _backend_instance = S3Backend()  # raises NotImplementedError
    return _backend_instance
