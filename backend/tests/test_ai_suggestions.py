"""Simplified Tests for AI Suggestions Module"""

import hashlib
import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai_suggestions.algorithms import (
    HybridSimilarity,
    KeywordSimilarity,
    LLMEmbeddingSimilarity,
    TFIDFSimilarity,
    compute_text_hash,
)
from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine
from app.models.base import Base
from app.models.embedding_cache import EmbeddingCache
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.requirement import (
    PriorityLevel,
    Requirement,
    RequirementStatus,
    RequirementType,
)
from app.models.test_case import (
    AutomationStatus,
    TestCase,
    TestCaseStatus,
    TestCaseType,
)

#  Algorithm Tests (No DB needed)


def test_keyword_similarity_basic():
    """Test basic keyword similarity computation"""
    algo = KeywordSimilarity(min_word_length=3, top_n=10)

    text1 = "The user should be able to login with username and password"
    text2 = "Test user login with valid username and password credentials"

    similarity = algo.compute_similarity(text1, text2)

    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.0


def test_keyword_similarity_identical():
    """Test keyword similarity with identical texts"""
    algo = KeywordSimilarity()

    text = "The system shall process payments"
    similarity = algo.compute_similarity(text, text)

    assert similarity == 1.0


def test_keyword_similarity_no_overlap():
    """Test keyword similarity with no common keywords"""
    algo = KeywordSimilarity()

    text1 = "database connection timeout"
    text2 = "user interface design"

    similarity = algo.compute_similarity(text1, text2)

    assert similarity == 0.0


def test_tfidf_similarity_basic():
    """Test TF-IDF similarity computation"""
    try:
        algo = TFIDFSimilarity(max_features=50, ngram_range=(1, 2))

        text1 = "The user should be able to login with username and password"
        text2 = "Test user authentication with username and password"

        similarity = algo.compute_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.0
    except ImportError:
        pytest.skip("scikit-learn not available")


def test_hybrid_similarity():
    """Test hybrid similarity algorithm"""
    algo = HybridSimilarity(tfidf_weight=0.6, keyword_weight=0.4)

    text1 = "User authentication with password"
    text2 = "Test user login with password"

    similarity = algo.compute_similarity(text1, text2)

    assert 0.0 <= similarity <= 1.0


def test_llm_embedding_similarity_openai_mock():
    """Test LLM embedding with OpenAI (mocked)"""
    # Mock the OpenAI module before creating the instance
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        # Mock at the module level
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        # Mock embedding response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        # Inject the mock into sys.modules before creating instance
        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            # Create algorithm and test
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=False)

            text1 = "User authentication with password"
            text2 = "Test user login with password"

            similarity = algo.compute_similarity(text1, text2)

            # Should return valid similarity score
            assert 0.0 <= similarity <= 1.0
            assert similarity == 1.0  # Normalized cosine similarity of identical vectors
        finally:
            # Clean up
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_embedding_similarity_caching():
    """Test that LLM embedding caching works"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            # Create algorithm with caching enabled
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)

            text = "Test text"

            # First call should hit the API
            algo.compute_similarity(text, text)
            assert mock_client.embeddings.create.call_count == 1

            # Second call should use cache
            algo.compute_similarity(text, text)
            assert mock_client.embeddings.create.call_count == 1  # Still 1, not 2
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_embedding_similarity_error_handling():
    """Test graceful fallback when LLM fails"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        # Make the API call raise an exception
        mock_client.embeddings.create.side_effect = Exception("API Error")

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=False)

            text1 = "User authentication"
            text2 = "Test login"

            # Should return 0.0 on error, not raise exception
            similarity = algo.compute_similarity(text1, text2)
            assert similarity == 0.0
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_embedding_similarity_empty_text():
    """Test LLM embedding with empty text"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_openai_module.OpenAI.return_value = MagicMock()

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            algo = LLMEmbeddingSimilarity(provider="openai")

            # Empty text should return 0.0
            assert algo.compute_similarity("", "test") == 0.0
            assert algo.compute_similarity("test", "") == 0.0
            assert algo.compute_similarity("", "") == 0.0
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_embedding_similarity_unsupported_provider():
    """Test that unsupported provider raises error"""
    with pytest.raises(ValueError, match="Unsupported provider"):
        LLMEmbeddingSimilarity(provider="unsupported")


def test_llm_embedding_similarity_missing_openai_library():
    """Test that missing OpenAI library raises ImportError"""
    import sys

    # Make sure openai is not in sys.modules
    if "openai" in sys.modules:
        del sys.modules["openai"]

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(ImportError, match="OpenAI library not installed"):
            LLMEmbeddingSimilarity(provider="openai")


def test_llm_get_embeddings_batch_openai():
    """Test that get_embeddings_batch returns embeddings in order and populates cache"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        emb_a = [0.1] * 1536
        emb_b = [0.2] * 1536

        def make_response(texts):
            embeddings = [emb_a if t == "text_a" else emb_b for t in texts]
            resp = MagicMock()
            resp.data = [MagicMock(embedding=e) for e in embeddings]
            return resp

        mock_client.embeddings.create.side_effect = lambda input, model: make_response(input)

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)

            texts = ["text_a", "text_b", "text_a"]
            result = algo.get_embeddings_batch(texts)

            # Correct order and values
            assert result[0] == emb_a
            assert result[1] == emb_b
            assert result[2] == emb_a  # duplicate resolved from cache

            # Cache should be populated
            assert algo._embedding_cache["text_a"] == emb_a
            assert algo._embedding_cache["text_b"] == emb_b

            # Only one API call (deduplication)
            assert mock_client.embeddings.create.call_count == 1
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_get_embeddings_batch_uses_cache():
    """Test that already-cached texts are not re-fetched"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.3] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)

            # Pre-populate cache for "cached_text"
            algo._embedding_cache["cached_text"] = [0.9] * 1536

            result = algo.get_embeddings_batch(["cached_text", "new_text"])

            # Cached text should return the cached value
            assert result[0] == [0.9] * 1536
            # New text fetched from API
            assert result[1] == [0.3] * 1536

            # API called only once for the new text
            assert mock_client.embeddings.create.call_count == 1
            call_args = mock_client.embeddings.create.call_args
            assert (
                call_args.kwargs["input"] == ["new_text"]
                or call_args.args[0] == ["new_text"]
                or "new_text" in str(call_args)
            )
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_get_embeddings_batch_chunking():
    """Test that batch embedding chunks input when it exceeds batch_size"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        def make_response(texts):
            resp = MagicMock()
            resp.data = [MagicMock(embedding=[float(i)] * 4) for i in range(len(texts))]
            return resp

        mock_client.embeddings.create.side_effect = lambda input, model: make_response(input)

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            # Use a small batch_size of 3
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True, batch_size=3)

            texts = [f"text_{i}" for i in range(7)]
            result = algo.get_embeddings_batch(texts)

            assert len(result) == 7

            # 7 unique texts with batch_size=3 → ceil(7/3) = 3 API calls
            assert mock_client.embeddings.create.call_count == 3
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


def test_llm_precompute_embeddings_warms_cache():
    """Test that precompute_embeddings populates the cache before pairwise computation"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        emb = [0.5] * 1536
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=emb), MagicMock(embedding=emb)]
        mock_client.embeddings.create.return_value = mock_response

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)

            texts = ["req text", "tc text"]
            algo.precompute_embeddings(texts)

            # Cache should be warm
            assert "req text" in algo._embedding_cache
            assert "tc text" in algo._embedding_cache

            api_calls_after_precompute = mock_client.embeddings.create.call_count

            # compute_similarity should not make additional API calls
            algo.compute_similarity("req text", "tc text")
            assert mock_client.embeddings.create.call_count == api_calls_after_precompute
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


# Engine Tests (with DB)


@pytest.mark.asyncio
async def test_engine_basic_flow():
    """Test complete suggestion generation flow"""
    # Create in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # Create sample data
        req = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-001",
            title="User Authentication",
            description="The system shall allow users to login",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
        )

        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test User Login",
            description="Verify that users can login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED,
        )

        session.add(req)
        session.add(tc)
        await session.commit()

        # Run suggestion generation
        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.1)
        sug_engine = SuggestionEngine(config=config)

        result = await sug_engine.generate_suggestions(session)

        # Verify results
        assert result["pairs_analyzed"] == 1
        assert result["suggestions_created"] >= 0
        assert result["algorithm_used"] == "keyword"

    await engine.dispose()


@pytest.mark.asyncio
async def test_engine_idempotency():
    """Test that running twice doesn't create duplicates"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        req = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-001",
            title="User Authentication",
            description="Login functionality",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
        )

        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test Login",
            description="Test user login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED,
        )

        session.add(req)
        session.add(tc)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.1)
        sug_engine = SuggestionEngine(config=config)

        # First run
        result1 = await sug_engine.generate_suggestions(session)
        first_created = result1["suggestions_created"]

        # Second run
        result2 = await sug_engine.generate_suggestions(session)
        second_created = result2["suggestions_created"]

        # Should create no new suggestions on second run
        assert second_created == 0
        if first_created > 0:
            assert result2["suggestions_skipped"] >= first_created

    await engine.dispose()


@pytest.mark.asyncio
async def test_engine_skips_existing_links():
    """Test that pairs with links are skipped"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        req = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-001",
            title="User Authentication",
            description="Login functionality",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
        )

        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test Login",
            description="Test user login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED,
        )

        # Create a link
        link = RequirementTestCaseLink(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
        )

        session.add(req)
        session.add(tc)
        session.add(link)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        result = await sug_engine.generate_suggestions(session)

        # Should skip the linked pair
        assert result["suggestions_skipped"] > 0
        assert result["suggestions_created"] == 0

    await engine.dispose()


# ── Embedding Cache Tests ──────────────────────────────────────────────────────


def test_compute_text_hash_deterministic():
    """compute_text_hash returns the same SHA-256 hex for the same text."""
    text = "hello world"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert compute_text_hash(text) == expected
    assert compute_text_hash(text) == compute_text_hash(text)


def test_compute_text_hash_different_texts():
    """Different texts produce different hashes."""
    assert compute_text_hash("text A") != compute_text_hash("text B")


@pytest.mark.asyncio
async def test_db_embedding_cache_save_and_retrieve():
    """Embeddings saved to the DB can be retrieved in a subsequent session."""
    from app.crud.embedding_cache import get_cached_embeddings_batch, save_embeddings_batch

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    text = "User authentication login"
    embedding = [0.1, 0.2, 0.3]
    text_hash = compute_text_hash(text)
    model_name = "text-embedding-3-small"

    async with AsyncSessionLocal() as session:
        await save_embeddings_batch(
            session,
            [{"text_hash": text_hash, "embedding": embedding, "model_name": model_name, "provider": "openai"}],
        )
        await session.commit()

    # New session — simulates a server restart
    async with AsyncSessionLocal() as session:
        hits = await get_cached_embeddings_batch(session, [text_hash], model_name)
        assert text_hash in hits
        assert hits[text_hash] == embedding

    await engine.dispose()


@pytest.mark.asyncio
async def test_db_embedding_cache_upsert():
    """Saving the same (text_hash, model_name) twice updates the embedding."""
    from app.crud.embedding_cache import get_cached_embeddings_batch, save_embeddings_batch

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    text_hash = compute_text_hash("some text")
    model_name = "text-embedding-3-small"

    async with AsyncSessionLocal() as session:
        await save_embeddings_batch(
            session,
            [{"text_hash": text_hash, "embedding": [0.1, 0.2], "model_name": model_name, "provider": "openai"}],
        )
        await session.commit()

    async with AsyncSessionLocal() as session:
        await save_embeddings_batch(
            session,
            [{"text_hash": text_hash, "embedding": [0.9, 0.8], "model_name": model_name, "provider": "openai"}],
        )
        await session.commit()

    async with AsyncSessionLocal() as session:
        hits = await get_cached_embeddings_batch(session, [text_hash], model_name)
        assert hits[text_hash] == [0.9, 0.8]

    await engine.dispose()


@pytest.mark.asyncio
async def test_db_embedding_cache_different_models():
    """The same text embedded by different models gets separate cache entries."""
    from app.crud.embedding_cache import get_cached_embeddings_batch, save_embeddings_batch

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    text_hash = compute_text_hash("some text")
    emb_small = [0.1, 0.2]
    emb_large = [0.3, 0.4]

    async with AsyncSessionLocal() as session:
        await save_embeddings_batch(
            session,
            [
                {
                    "text_hash": text_hash,
                    "embedding": emb_small,
                    "model_name": "text-embedding-3-small",
                    "provider": "openai",
                },
                {
                    "text_hash": text_hash,
                    "embedding": emb_large,
                    "model_name": "text-embedding-3-large",
                    "provider": "openai",
                },
            ],
        )
        await session.commit()

    async with AsyncSessionLocal() as session:
        hits_small = await get_cached_embeddings_batch(session, [text_hash], "text-embedding-3-small")
        hits_large = await get_cached_embeddings_batch(session, [text_hash], "text-embedding-3-large")

    assert hits_small[text_hash] == emb_small
    assert hits_large[text_hash] == emb_large

    await engine.dispose()


@pytest.mark.asyncio
async def test_db_embedding_cache_delete_stale():
    """delete_stale_embeddings removes old entries and returns the deleted count."""
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import update

    from app.crud.embedding_cache import delete_stale_embeddings, save_embeddings_batch

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await save_embeddings_batch(
            session,
            [
                {
                    "text_hash": compute_text_hash("old text"),
                    "embedding": [0.1],
                    "model_name": "m",
                    "provider": "openai",
                },
                {
                    "text_hash": compute_text_hash("new text"),
                    "embedding": [0.2],
                    "model_name": "m",
                    "provider": "openai",
                },
            ],
        )
        await session.commit()

    # Back-date the "old text" entry so it looks stale
    old_hash = compute_text_hash("old text")
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(EmbeddingCache)
            .where(EmbeddingCache.text_hash == old_hash)
            .values(updated_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=100))
        )
        await session.commit()

    async with AsyncSessionLocal() as session:
        deleted = await delete_stale_embeddings(session, older_than_days=90)
        await session.commit()

    assert deleted == 1

    await engine.dispose()


@pytest.mark.asyncio
async def test_llm_load_cached_embeddings_populates_in_memory_cache():
    """load_cached_embeddings fetches DB hits and warms the in-memory cache."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)
            text = "pre-cached requirement text"
            stored_embedding = [0.7] * 1536
            text_hash = compute_text_hash(text)

            # Pre-populate the DB cache
            from app.crud.embedding_cache import save_embeddings_batch

            async with AsyncSessionLocal() as session:
                await save_embeddings_batch(
                    session,
                    [
                        {
                            "text_hash": text_hash,
                            "embedding": stored_embedding,
                            "model_name": algo.model,
                            "provider": "openai",
                        }
                    ],
                )
                await session.commit()

            # load_cached_embeddings should populate in-memory cache from DB
            async with AsyncSessionLocal() as session:
                hits = await algo.load_cached_embeddings(session, [text])

            assert text in hits
            assert hits[text] == stored_embedding
            assert algo._embedding_cache[text] == stored_embedding

            # precompute_embeddings should NOT call the API for the cached text
            algo.precompute_embeddings([text])
            assert mock_client.embeddings.create.call_count == 0

            await engine.dispose()
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


@pytest.mark.asyncio
async def test_llm_save_embeddings_to_db():
    """save_embeddings_to_db persists in-memory cached embeddings to the DB."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        embedding = [0.5] * 8
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=embedding)]
        mock_client.embeddings.create.return_value = mock_response

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

            algo = LLMEmbeddingSimilarity(provider="openai", cache_embeddings=True)
            text = "requirement to embed"

            # Compute embedding (warms in-memory cache)
            algo.precompute_embeddings([text])

            # Persist to DB
            async with AsyncSessionLocal() as session:
                await algo.save_embeddings_to_db(session, [text])
                await session.commit()

            # Verify DB has the entry
            from app.crud.embedding_cache import get_cached_embeddings_batch

            async with AsyncSessionLocal() as session:
                hits = await get_cached_embeddings_batch(session, [compute_text_hash(text)], algo.model)

            assert compute_text_hash(text) in hits
            assert hits[compute_text_hash(text)] == embedding

            await engine.dispose()
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]


@pytest.mark.asyncio
async def test_engine_llm_uses_db_cache_on_second_run():
    """Second generate_suggestions run with LLM loads embeddings from DB, skipping API calls."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        mock_openai_module = MagicMock()
        mock_client = MagicMock()
        mock_openai_module.OpenAI.return_value = mock_client

        emb = [0.5] * 8
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=emb), MagicMock(embedding=emb)]
        mock_client.embeddings.create.return_value = mock_response

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            db_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
            async with db_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            AsyncSessionLocal = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

            req = Requirement(
                id=uuid.uuid4(),
                external_id="REQ-LLM-01",
                title="Authentication requirement",
                description="Users must authenticate",
                type=RequirementType.FUNCTIONAL,
                priority=PriorityLevel.HIGH,
                status=RequirementStatus.APPROVED,
            )
            tc = TestCase(
                id=uuid.uuid4(),
                external_id="TC-LLM-01",
                title="Test authentication",
                description="Verify login flow",
                type=TestCaseType.FUNCTIONAL,
                priority=PriorityLevel.HIGH,
                status=TestCaseStatus.READY,
                automation_status=AutomationStatus.AUTOMATED,
            )

            async with AsyncSessionLocal() as session:
                session.add(req)
                session.add(tc)
                await session.commit()

            config = SuggestionConfig(
                default_algorithm="llm",
                min_confidence_threshold=0.0,
                llm_db_cache_enabled=True,
            )

            # First run: embeddings computed via API and persisted to DB
            async with AsyncSessionLocal() as session:
                sug_engine = SuggestionEngine(config=config)
                await sug_engine.generate_suggestions(session)

            api_calls_after_first_run = mock_client.embeddings.create.call_count
            assert api_calls_after_first_run >= 1

            # Second run: embeddings should be loaded from DB — no new API calls
            async with AsyncSessionLocal() as session:
                sug_engine2 = SuggestionEngine(config=config)
                await sug_engine2.generate_suggestions(session)

            assert mock_client.embeddings.create.call_count == api_calls_after_first_run

            await db_engine.dispose()
        finally:
            if "openai" in sys.modules:
                del sys.modules["openai"]
