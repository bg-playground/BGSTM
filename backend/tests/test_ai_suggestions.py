"""Simplified Tests for AI Suggestions Module"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models.base import Base
from app.models.requirement import Requirement, RequirementType, PriorityLevel, RequirementStatus
from app.models.test_case import TestCase, TestCaseType, TestCaseStatus, AutomationStatus
from app.models.link import RequirementTestCaseLink, LinkType, LinkSource
from app.models.suggestion import LinkSuggestion, SuggestionStatus
from app.ai_suggestions.algorithms import TFIDFSimilarity, KeywordSimilarity, HybridSimilarity
from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine


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
            status=RequirementStatus.APPROVED
        )
        
        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test User Login",
            description="Verify that users can login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED
        )
        
        session.add(req)
        session.add(tc)
        await session.commit()
        
        # Run suggestion generation
        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.1)
        sug_engine = SuggestionEngine(config=config)
        
        result = await sug_engine.generate_suggestions(session)
        
        # Verify results
        assert result['pairs_analyzed'] == 1
        assert result['suggestions_created'] >= 0
        assert result['algorithm_used'] == 'keyword'
    
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
            status=RequirementStatus.APPROVED
        )
        
        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test Login",
            description="Test user login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED
        )
        
        session.add(req)
        session.add(tc)
        await session.commit()
        
        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.1)
        sug_engine = SuggestionEngine(config=config)
        
        # First run
        result1 = await sug_engine.generate_suggestions(session)
        first_created = result1['suggestions_created']
        
        # Second run
        result2 = await sug_engine.generate_suggestions(session)
        second_created = result2['suggestions_created']
        
        # Should create no new suggestions on second run
        assert second_created == 0
        if first_created > 0:
            assert result2['suggestions_skipped'] >= first_created
    
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
            status=RequirementStatus.APPROVED
        )
        
        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test Login",
            description="Test user login",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.AUTOMATED
        )
        
        # Create a link
        link = RequirementTestCaseLink(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL
        )
        
        session.add(req)
        session.add(tc)
        session.add(link)
        await session.commit()
        
        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)
        
        result = await sug_engine.generate_suggestions(session)
        
        # Should skip the linked pair
        assert result['suggestions_skipped'] > 0
        assert result['suggestions_created'] == 0
    
    await engine.dispose()

