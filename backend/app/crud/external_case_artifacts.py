"""CRUD operations for External Case Artifacts (BGSTM#298)."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_case_artifact import ArtifactKind, ExternalCaseArtifact


async def create_artifact(
    db: AsyncSession,
    *,
    case_result_id: UUID,
    kind: ArtifactKind,
    filename: str,
    content_type: str,
    size_bytes: int,
    storage_key: str,
    url: str,
) -> ExternalCaseArtifact:
    """Persist an artifact record linked to *case_result_id*.

    Does **not** commit the session — callers are responsible for committing.
    """
    artifact = ExternalCaseArtifact(
        id=uuid.uuid4(),
        case_result_id=case_result_id,
        kind=kind,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
        storage_key=storage_key,
        url=url,
    )
    db.add(artifact)
    await db.flush()
    await db.refresh(artifact)
    return artifact
