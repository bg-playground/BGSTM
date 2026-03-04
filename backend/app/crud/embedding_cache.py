"""CRUD operations for the persistent embedding cache"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding_cache import EmbeddingCache


async def get_cached_embedding(db: AsyncSession, text_hash: str, model_name: str) -> list[float] | None:
    """Return the cached embedding for a single (text_hash, model_name) pair, or None on miss."""
    result = await db.execute(
        select(EmbeddingCache.embedding).where(
            EmbeddingCache.text_hash == text_hash,
            EmbeddingCache.model_name == model_name,
        )
    )
    row = result.scalar_one_or_none()
    return row


async def get_cached_embeddings_batch(
    db: AsyncSession, text_hashes: list[str], model_name: str
) -> dict[str, list[float]]:
    """
    Return a mapping of text_hash → embedding for all cache hits.

    Any text_hash not present in the DB is simply omitted from the result.
    """
    if not text_hashes:
        return {}
    result = await db.execute(
        select(EmbeddingCache.text_hash, EmbeddingCache.embedding).where(
            EmbeddingCache.text_hash.in_(text_hashes),
            EmbeddingCache.model_name == model_name,
        )
    )
    return {row.text_hash: row.embedding for row in result}


async def save_embedding(
    db: AsyncSession,
    text_hash: str,
    embedding: list[float],
    model_name: str,
    provider: str,
) -> None:
    """Upsert a single embedding into the cache (insert or update on conflict)."""
    await save_embeddings_batch(
        db,
        [
            {
                "text_hash": text_hash,
                "embedding": embedding,
                "model_name": model_name,
                "provider": provider,
            }
        ],
    )


async def save_embeddings_batch(db: AsyncSession, entries: list[dict]) -> None:
    """
    Upsert a batch of embeddings into the cache.

    Each entry dict must contain: text_hash, embedding, model_name, provider.
    On conflict (text_hash, model_name) the embedding and updated_at are refreshed.
    """
    if not entries:
        return

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for entry in entries:
        embedding: list[float] = entry["embedding"]
        row = EmbeddingCache(
            text_hash=entry["text_hash"],
            embedding=embedding,
            model_name=entry["model_name"],
            provider=entry["provider"],
            dimensions=len(embedding),
            created_at=now,
            updated_at=now,
        )
        # Use merge (upsert by unique constraint) — works across SQLite and PostgreSQL.
        # SQLAlchemy's Session.merge matches on primary key, so we look up existing first.
        existing_result = await db.execute(
            select(EmbeddingCache).where(
                EmbeddingCache.text_hash == entry["text_hash"],
                EmbeddingCache.model_name == entry["model_name"],
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            existing.embedding = embedding
            existing.dimensions = len(embedding)
            existing.updated_at = now
        else:
            db.add(row)

    await db.flush()


async def delete_stale_embeddings(db: AsyncSession, older_than_days: int = 90) -> int:
    """
    Delete embeddings that haven't been accessed/updated in *older_than_days* days.

    Returns the number of rows deleted.
    """
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=older_than_days)
    result = await db.execute(delete(EmbeddingCache).where(EmbeddingCache.updated_at < cutoff))
    await db.flush()
    return result.rowcount
