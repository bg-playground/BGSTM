"""
ShopFlow E-Commerce Sample Data Loader
=======================================
This module loads sample data for an e-commerce platform called "ShopFlow".

Sample Data:
- 5 Requirements (user authentication, product search, shopping cart, checkout, order tracking)
- 4 Test Cases covering various functionalities
- Manual links between requirements and test cases
"""

import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal, init_db
from app.models.requirement import Requirement, RequirementType, PriorityLevel, RequirementStatus
from app.models.test_case import TestCase, TestCaseType, TestCaseStatus, AutomationStatus
from app.models.link import RequirementTestCaseLink, LinkType, LinkSource


async def load_sample_data():
    """Load ShopFlow sample data into the database"""
    print("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        print("Loading ShopFlow sample data...")
        
        # Create Requirements
        req1 = Requirement(
            external_id="REQ-001",
            title="User Authentication System",
            description="Implement secure user authentication with email/password login, OAuth support (Google, Facebook), "
                       "password reset functionality, and session management. Must include 2FA option.",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
            status=RequirementStatus.APPROVED,
            module="Authentication",
            tags=["security", "user-management", "login"],
            custom_metadata={"complexity": "high", "estimated_hours": 40},
            source_system="Jira",
            created_by="product_manager"
        )
        
        req2 = Requirement(
            external_id="REQ-002",
            title="Product Search and Filtering",
            description="Advanced product search with filters for category, price range, brand, ratings, and availability. "
                       "Include autocomplete suggestions and search history.",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
            module="Product",
            tags=["search", "filtering", "user-experience"],
            custom_metadata={"complexity": "medium", "estimated_hours": 24},
            source_system="Jira",
            created_by="product_manager"
        )
        
        req3 = Requirement(
            external_id="REQ-003",
            title="Shopping Cart Management",
            description="Users can add/remove items, update quantities, save cart for later, and apply discount codes. "
                       "Cart should persist across sessions and devices.",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.IMPLEMENTED,
            module="Cart",
            tags=["shopping-cart", "user-experience", "persistence"],
            custom_metadata={"complexity": "medium", "estimated_hours": 20},
            source_system="Jira",
            created_by="product_manager"
        )
        
        req4 = Requirement(
            external_id="REQ-004",
            title="Secure Checkout Process",
            description="Multi-step checkout with address validation, payment processing (credit card, PayPal, Apple Pay), "
                       "order summary, and confirmation email. PCI DSS compliant.",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
            status=RequirementStatus.TESTED,
            module="Checkout",
            tags=["payment", "security", "checkout"],
            custom_metadata={"complexity": "high", "estimated_hours": 50},
            source_system="Jira",
            created_by="product_manager"
        )
        
        req5 = Requirement(
            external_id="REQ-005",
            title="Order Tracking and History",
            description="Users can view order history, track current orders with real-time updates, download invoices, "
                       "and request returns/refunds.",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=RequirementStatus.DRAFT,
            module="Orders",
            tags=["order-management", "tracking", "user-experience"],
            custom_metadata={"complexity": "medium", "estimated_hours": 30},
            source_system="Jira",
            created_by="product_manager"
        )
        
        session.add_all([req1, req2, req3, req4, req5])
        await session.flush()  # Get IDs
        
        # Create Test Cases
        tc1 = TestCase(
            external_id="TC-001",
            title="Verify User Login with Valid Credentials",
            description="Test successful login flow with valid email and password. Verify session creation, "
                       "user dashboard access, and proper token generation.",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.CRITICAL,
            status=TestCaseStatus.PASSED,
            steps={
                "1": "Navigate to login page",
                "2": "Enter valid email address",
                "3": "Enter valid password",
                "4": "Click 'Login' button",
                "5": "Verify redirection to dashboard"
            },
            preconditions="User account exists in the database",
            postconditions="User is logged in and session is active",
            test_data={"email": "test@example.com", "password": "Test@123"},
            module="Authentication",
            tags=["login", "smoke-test", "critical"],
            automation_status=AutomationStatus.AUTOMATED,
            execution_time_minutes=5,
            source_system="TestRail",
            created_by="qa_engineer"
        )
        
        tc2 = TestCase(
            external_id="TC-002",
            title="Verify Product Search with Multiple Filters",
            description="Test product search functionality with multiple filters applied simultaneously. "
                       "Verify correct results, pagination, and performance.",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            steps={
                "1": "Navigate to products page",
                "2": "Enter search term 'laptop'",
                "3": "Apply price filter: $500-$1500",
                "4": "Apply brand filter: 'Dell'",
                "5": "Apply rating filter: 4+ stars",
                "6": "Verify filtered results match criteria"
            },
            preconditions="Product catalog is populated with test data",
            postconditions="Search results display correct products",
            test_data={
                "search_term": "laptop",
                "price_min": 500,
                "price_max": 1500,
                "brand": "Dell",
                "min_rating": 4
            },
            module="Product",
            tags=["search", "filtering", "regression"],
            automation_status=AutomationStatus.AUTOMATABLE,
            execution_time_minutes=10,
            source_system="TestRail",
            created_by="qa_engineer"
        )
        
        tc3 = TestCase(
            external_id="TC-003",
            title="Verify Shopping Cart Operations",
            description="Test complete shopping cart lifecycle: add items, update quantities, remove items, "
                       "apply discount code, and verify cart persistence.",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.PASSED,
            steps={
                "1": "Add product to cart",
                "2": "Verify product appears in cart",
                "3": "Update quantity to 3",
                "4": "Apply discount code 'SAVE10'",
                "5": "Verify price calculation",
                "6": "Remove one item",
                "7": "Verify cart total updates"
            },
            preconditions="User is logged in, products available",
            postconditions="Cart reflects all changes accurately",
            test_data={
                "product_id": "PROD-123",
                "discount_code": "SAVE10",
                "discount_percent": 10
            },
            module="Cart",
            tags=["cart", "e2e", "regression"],
            automation_status=AutomationStatus.AUTOMATED,
            execution_time_minutes=8,
            source_system="TestRail",
            created_by="qa_engineer"
        )
        
        tc4 = TestCase(
            external_id="TC-004",
            title="Verify End-to-End Checkout Process",
            description="Test complete checkout flow from cart to order confirmation. Includes address entry, "
                       "payment processing, and confirmation email.",
            type=TestCaseType.INTEGRATION,
            priority=PriorityLevel.CRITICAL,
            status=TestCaseStatus.PASSED,
            steps={
                "1": "Navigate to cart with items",
                "2": "Click 'Proceed to Checkout'",
                "3": "Enter shipping address",
                "4": "Select shipping method",
                "5": "Enter payment information",
                "6": "Review order summary",
                "7": "Click 'Place Order'",
                "8": "Verify confirmation page",
                "9": "Check confirmation email"
            },
            preconditions="Cart has items, test payment method available",
            postconditions="Order created, confirmation email sent",
            test_data={
                "card_number": "4111111111111111",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "zip": "12345"
                }
            },
            module="Checkout",
            tags=["checkout", "payment", "e2e", "critical"],
            automation_status=AutomationStatus.AUTOMATED,
            execution_time_minutes=15,
            source_system="TestRail",
            created_by="qa_engineer"
        )
        
        session.add_all([tc1, tc2, tc3, tc4])
        await session.flush()
        
        # Create Manual Links
        link1 = RequirementTestCaseLink(
            requirement_id=req1.id,
            test_case_id=tc1.id,
            link_type=LinkType.COVERS,
            confidence_score=1.0,
            link_source=LinkSource.MANUAL,
            created_by="qa_engineer",
            notes="Direct coverage of login functionality"
        )
        
        link2 = RequirementTestCaseLink(
            requirement_id=req2.id,
            test_case_id=tc2.id,
            link_type=LinkType.VERIFIES,
            confidence_score=1.0,
            link_source=LinkSource.MANUAL,
            created_by="qa_engineer",
            notes="Verifies search and filtering requirements"
        )
        
        link3 = RequirementTestCaseLink(
            requirement_id=req3.id,
            test_case_id=tc3.id,
            link_type=LinkType.COVERS,
            confidence_score=1.0,
            link_source=LinkSource.MANUAL,
            created_by="qa_engineer",
            notes="Covers all cart operations"
        )
        
        link4 = RequirementTestCaseLink(
            requirement_id=req4.id,
            test_case_id=tc4.id,
            link_type=LinkType.VALIDATES,
            confidence_score=1.0,
            link_source=LinkSource.MANUAL,
            created_by="qa_engineer",
            notes="End-to-end validation of checkout process"
        )
        
        link5 = RequirementTestCaseLink(
            requirement_id=req3.id,
            test_case_id=tc4.id,
            link_type=LinkType.RELATED,
            confidence_score=0.8,
            link_source=LinkSource.MANUAL,
            created_by="qa_engineer",
            notes="Checkout depends on cart functionality"
        )
        
        session.add_all([link1, link2, link3, link4, link5])
        
        await session.commit()
        
        print("✅ Sample data loaded successfully!")
        print(f"  - {5} Requirements created")
        print(f"  - {4} Test Cases created")
        print(f"  - {5} Manual Links created")


if __name__ == "__main__":
    asyncio.run(load_sample_data())
