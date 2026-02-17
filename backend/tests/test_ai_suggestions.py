"""Tests for AI Suggestions Module"""

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


# Database fixture for testing
@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def sample_requirements(db_session):
    """Create sample requirements for testing"""
    requirements = [
        Requirement(
            id=uuid.uuid4(),
            external_id="REQ-001",
            title="User Authentication",
            description="The system shall allow users to login with username and password",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
            module="Authentication",
            tags=["security", "login", "user"]
        ),
        Requirement(
            id=uuid.uuid4(),
            external_id="REQ-002",
            title="Product Search",
            description="The system shall provide a search functionality for products with filters",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=RequirementStatus.APPROVED,
            module="Search",
            tags=["search", "product", "filter"]
        ),
        Requirement(
            id=uuid.uuid4(),
            external_id="REQ-003",
            title="Payment Processing",
            description="The system shall process credit card payments securely",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
            status=RequirementStatus.APPROVED,
            module="Payment",
            tags=["payment", "security", "transaction"]
        )
    ]
    
    for req in requirements:
        db_session.add(req)
    await db_session.commit()
    
    return requirements


@pytest.fixture
async def sample_test_cases(db_session):
    """Create sample test cases for testing"""
    test_cases = [
        TestCase(
            id=uuid.uuid4(),
            external_id="TC-001",
            title="Test User Login",
            description="Verify that users can login with valid credentials",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            preconditions="User account exists",
            postconditions="User is logged in",
            steps=["Enter username", "Enter password", "Click login"],
            module="Authentication",
            tags=["authentication", "login"],
            automation_status=AutomationStatus.AUTOMATED
        ),
        TestCase(
            id=uuid.uuid4(),
            external_id="TC-002",
            title="Test Product Search",
            description="Verify that users can search for products and apply filters",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=TestCaseStatus.READY,
            preconditions="User is on homepage",
            postconditions="Search results are displayed",
            steps=["Enter search term", "Apply filters", "Verify results"],
            module="Search",
            tags=["search", "product"],
            automation_status=AutomationStatus.AUTOMATED
        ),
        TestCase(
            id=uuid.uuid4(),
            external_id="TC-003",
            title="Test Payment Flow",
            description="Verify that payment can be processed with credit card",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
            status=TestCaseStatus.READY,
            preconditions="User has items in cart",
            postconditions="Payment is processed successfully",
            steps=["Enter credit card details", "Submit payment", "Verify confirmation"],
            module="Payment",
            tags=["payment", "credit card"],
            automation_status=AutomationStatus.AUTOMATED
        ),
        TestCase(
            id=uuid.uuid4(),
            external_id="TC-004",
            title="Test Logout",
            description="Verify that users can logout successfully",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.LOW,
            status=TestCaseStatus.READY,
            preconditions="User is logged in",
            postconditions="User is logged out",
            steps=["Click logout button", "Verify redirect to login page"],
            module="Authentication",
            tags=["authentication", "logout"],
            automation_status=AutomationStatus.MANUAL
        )
    ]
    
    for tc in test_cases:
        db_session.add(tc)
    await db_session.commit()
    
    return test_cases


# Algorithm Tests

def test_keyword_similarity_basic():
    """Test basic keyword similarity computation"""
    algo = KeywordSimilarity(min_word_length=3, top_n=10)
    
    text1 = "The user should be able to login with username and password"
    text2 = "Test user login with valid username and password credentials"
    
    similarity = algo.compute_similarity(text1, text2)
    
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.0  # Should find common keywords


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


def test_keyword_extract():
    """Test keyword extraction"""
    algo = KeywordSimilarity(min_word_length=3, top_n=5)
    
    text = "The system shall allow users to login with username and password for authentication"
    keywords = algo.extract_keywords(text)
    
    assert len(keywords) <= 5
    assert "users" in keywords or "login" in keywords or "password" in keywords
    assert "the" not in keywords  # Stop word should be filtered


def test_tfidf_similarity_basic():
    """Test TF-IDF similarity computation"""
    try:
        algo = TFIDFSimilarity(max_features=50, ngram_range=(1, 2))
        
        text1 = "The user should be able to login with username and password"
        text2 = "Test user authentication with username and password"
        
        similarity = algo.compute_similarity(text1, text2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.0  # Should find similarity
    except ImportError:
        pytest.skip("scikit-learn not available")


def test_tfidf_similarity_identical():
    """Test TF-IDF similarity with identical texts"""
    try:
        algo = TFIDFSimilarity()
        
        text = "The system shall process credit card payments securely"
        similarity = algo.compute_similarity(text, text)
        
        assert similarity == 1.0
    except ImportError:
        pytest.skip("scikit-learn not available")


def test_hybrid_similarity():
    """Test hybrid similarity algorithm"""
    algo = HybridSimilarity(tfidf_weight=0.6, keyword_weight=0.4)
    
    text1 = "User authentication with password"
    text2 = "Test user login with password"
    
    similarity = algo.compute_similarity(text1, text2)
    
    assert 0.0 <= similarity <= 1.0


def test_empty_text_handling():
    """Test that algorithms handle empty text gracefully"""
    algo = KeywordSimilarity()
    
    assert algo.compute_similarity("", "test") == 0.0
    assert algo.compute_similarity("test", "") == 0.0
    assert algo.compute_similarity("", "") == 0.0


# Engine Tests

@pytest.mark.asyncio
async def test_engine_initialization():
    """Test that engine initializes correctly"""
    config = SuggestionConfig(default_algorithm="keyword")
    engine = SuggestionEngine(config=config)
    
    assert engine.config == config
    assert engine.algorithm is not None


@pytest.mark.asyncio
async def test_engine_text_combination(sample_requirements, sample_test_cases):
    """Test that engine correctly combines text fields"""
    engine = SuggestionEngine()
    
    requirement = sample_requirements[0]
    test_case = sample_test_cases[0]
    
    req_text = engine._combine_text(requirement)
    tc_text = engine._combine_test_case_text(test_case)
    
    assert requirement.title in req_text
    assert requirement.description in req_text
    assert test_case.title in tc_text
    assert test_case.description in tc_text


@pytest.mark.asyncio
async def test_engine_compute_similarity(sample_requirements, sample_test_cases):
    """Test similarity computation between requirement and test case"""
    config = SuggestionConfig(default_algorithm="keyword")
    engine = SuggestionEngine(config=config)
    
    # REQ-001 (User Authentication) should match TC-001 (Test User Login)
    similarity = engine.compute_similarity(sample_requirements[0], sample_test_cases[0])
    
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.0  # Should have some similarity


@pytest.mark.asyncio
async def test_generate_suggestions_basic(db_session, sample_requirements, sample_test_cases):
    """Test basic suggestion generation"""
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.1  # Low threshold to ensure some suggestions
    )
    engine = SuggestionEngine(config=config)
    
    result = await engine.generate_suggestions(db_session)
    
    assert result['pairs_analyzed'] > 0
    assert result['suggestions_created'] >= 0
    assert result['algorithm_used'] == 'keyword'


@pytest.mark.asyncio
async def test_generate_suggestions_threshold_filtering(db_session, sample_requirements, sample_test_cases):
    """Test that suggestions are filtered by threshold"""
    # First run with low threshold
    config_low = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.1
    )
    engine_low = SuggestionEngine(config=config_low)
    result_low = await engine.generate_suggestions(db_session)
    
    # Clear suggestions
    from sqlalchemy import delete
    await db_session.execute(delete(LinkSuggestion))
    await db_session.commit()
    
    # Run with high threshold
    config_high = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.9
    )
    engine_high = SuggestionEngine(config=config_high)
    result_high = await engine_high.generate_suggestions(db_session)
    
    # High threshold should create fewer or equal suggestions
    assert result_high['suggestions_created'] <= result_low['suggestions_created']


@pytest.mark.asyncio
async def test_generate_suggestions_idempotency(db_session, sample_requirements, sample_test_cases):
    """Test that running suggestion generation twice doesn't create duplicates"""
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.1
    )
    engine = SuggestionEngine(config=config)
    
    # First run
    result1 = await engine.generate_suggestions(db_session)
    first_created = result1['suggestions_created']
    
    # Second run
    result2 = await engine.generate_suggestions(db_session)
    second_created = result2['suggestions_created']
    
    # Second run should create 0 new suggestions (all should be skipped)
    assert second_created == 0
    assert result2['suggestions_skipped'] >= first_created


@pytest.mark.asyncio
async def test_generate_suggestions_skips_existing_links(db_session, sample_requirements, sample_test_cases):
    """Test that pairs with existing links are skipped"""
    # Create a manual link
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=sample_requirements[0].id,
        test_case_id=sample_test_cases[0].id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
        created_by="test_user"
    )
    db_session.add(link)
    await db_session.commit()
    
    # Run suggestion generation
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.0  # Accept all pairs
    )
    engine = SuggestionEngine(config=config)
    result = await engine.generate_suggestions(db_session)
    
    # Verify the linked pair was skipped
    assert result['suggestions_skipped'] > 0
    
    # Check that no suggestion was created for the linked pair
    from sqlalchemy import select
    stmt = select(LinkSuggestion).where(
        LinkSuggestion.requirement_id == sample_requirements[0].id,
        LinkSuggestion.test_case_id == sample_test_cases[0].id
    )
    result_query = await db_session.execute(stmt)
    suggestion = result_query.scalar_one_or_none()
    
    assert suggestion is None


@pytest.mark.asyncio
async def test_suggestion_metadata(db_session, sample_requirements, sample_test_cases):
    """Test that suggestions include correct metadata"""
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.1
    )
    engine = SuggestionEngine(config=config)
    
    await engine.generate_suggestions(db_session)
    
    # Fetch a suggestion
    from sqlalchemy import select
    stmt = select(LinkSuggestion).limit(1)
    result = await db_session.execute(stmt)
    suggestion = result.scalar_one_or_none()
    
    if suggestion:
        assert suggestion.similarity_score >= 0.1
        assert suggestion.suggestion_method is not None
        assert suggestion.suggestion_reason is not None
        assert suggestion.suggestion_metadata is not None
        assert 'algorithm' in suggestion.suggestion_metadata
        assert suggestion.status == SuggestionStatus.PENDING


@pytest.mark.asyncio
async def test_generate_suggestions_specific_requirements(db_session, sample_requirements, sample_test_cases):
    """Test generating suggestions for specific requirements only"""
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.0
    )
    engine = SuggestionEngine(config=config)
    
    # Generate for only first requirement
    result = await engine.generate_suggestions(
        db_session,
        requirement_ids=[sample_requirements[0].id]
    )
    
    # Should analyze only N pairs where N = number of test cases
    assert result['pairs_analyzed'] == len(sample_test_cases)


@pytest.mark.asyncio
async def test_generate_suggestions_specific_test_cases(db_session, sample_requirements, sample_test_cases):
    """Test generating suggestions for specific test cases only"""
    config = SuggestionConfig(
        default_algorithm="keyword",
        min_confidence_threshold=0.0
    )
    engine = SuggestionEngine(config=config)
    
    # Generate for only first test case
    result = await engine.generate_suggestions(
        db_session,
        test_case_ids=[sample_test_cases[0].id]
    )
    
    # Should analyze only M pairs where M = number of requirements
    assert result['pairs_analyzed'] == len(sample_requirements)
