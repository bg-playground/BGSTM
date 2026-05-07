"""CRUD operations for External Case Artifacts (BGSTM#298)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_artifact import ArtifactKind, ExternalCaseArtifact


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
    runner_token_id: UUID,
) -> ExternalCaseArtifact:
    """Persist an artifact row and return it.

    # TODO(#297): Write audit entry ``external_results.artifact.upload`` here.
    """
    artifact = ExternalCaseArtifact(
        case_result_id=case_result_id,
        kind=kind,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
        storage_key=storage_key,
        url=url,
        runner_token_id=runner_token_id,
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact
