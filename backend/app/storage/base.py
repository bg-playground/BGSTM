"""Storage backend ABC for artifact uploads (BGSTM#298)."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    """Abstract interface for artifact storage backends."""

    @abstractmethod
    async def put(self, key: str, body: BinaryIO, content_type: str) -> str:
        """Store the object and return its URL.

        Args:
            key: Storage key / path (e.g. ``external-artifacts/uuid/file.png``).
            body: Readable binary stream positioned at the start.
            content_type: MIME type of the object.

        Returns:
            A fetchable URL for the stored object.
        """

    @abstractmethod
    async def url_for(self, key: str, expires_in: int = 3600) -> str:
        """Return a fetchable URL for the stored key.

        Args:
            key: Storage key previously passed to ``put``.
            expires_in: For signed-URL backends, validity window in seconds.
                        Ignored by permanent-URL backends (e.g. LocalFsBackend).

        Returns:
            A fetchable URL for the object.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the stored object.

        Args:
            key: Storage key previously passed to ``put``.
        """
