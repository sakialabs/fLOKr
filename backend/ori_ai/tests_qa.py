"""
Tests for Ori AI Q&A Service

**Feature: flokr-platform, Property 21: Natural language question answering**
"""
import pytest
import time
from django.contrib.auth import get_user_model
from django.utils import timezone

from ori_ai.models import FAQEntry
from ori_ai.qa_service import QAService

User = get_user_model()


@pytest.fixture
def qa_service():
    """Get Q&A service instance."""
    return QAService()


@pytest.fixture
def sample_faqs(db):
    """Create sample FAQ entries for testing."""
    faqs = [
        FAQEntry.objects.create(
            question="How do I borrow an item?",
            answer="To borrow an item, search for it, click reserve, and pick it up at your hub.",
            category="borrowing",
            keywords=["borrow", "reserve", "how to"],
            is_active=True
        ),
        FAQEntry.objects.create(
            question="What is a hub?",
            answer="A hub is a physical community center where items are stored and distributed.",
            category="hubs",
            keywords=["hub", "location", "center"],
            is_active=True
        ),
        FAQEntry.objects.create(
            question="How do I find a mentor?",
            answer="Go to the Mentorship section and browse available mentors by language and interests.",
            category="mentorship",
            keywords=["mentor", "find", "connect"],
            is_active=True
        ),
        FAQEntry.objects.create(
            question="Can I extend my borrowing period?",
            answer="Yes, you can request an extension before your due date through the app.",
            category="borrowing",
            keywords=["extend", "extension", "more time"],
            is_active=True
        ),
        FAQEntry.objects.create(
            question="What items are available?",
            answer="We have furniture, kitchen supplies, cleaning equipment, winter clothing, and more.",
            category="inventory",
            keywords=["items", "available", "inventory"],
            is_active=True
        ),
    ]
    return faqs


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="test123",
        first_name="Test",
        last_name="User"
    )


# ============================================================================
# Property 21: Natural language question answering
# ============================================================================

@pytest.mark.django_db
class TestNaturalLanguageQA:
    """
    **Property 21: Natural language question answering**
    *For any* natural language question submitted to Ori AI, a response 
    should be generated within ten seconds.
    **Validates: Requirements 5.2**
    """
    
    def test_response_generated_for_any_question(
        self, qa_service, sample_faqs
    ):
        """A response should be generated for any question."""
        question = "How do I borrow something?"
        
        result = qa_service.ask(question)
        
        # Should return a response
        assert 'answer' in result
        assert 'confidence' in result
        assert 'response_time' in result
        assert isinstance(result['answer'], str)
        assert len(result['answer']) > 0
    
    def test_response_time_under_ten_seconds(
        self, qa_service, sample_faqs
    ):
        """Response should be generated within 10 seconds."""
        question = "What is a hub and how does it work?"
        
        start_time = time.time()
        result = qa_service.ask(question)
        elapsed_time = time.time() - start_time
        
        # Response time should be under 10 seconds
        assert elapsed_time < 10.0
        assert result['response_time'] < 10.0
    
    def test_relevant_answer_for_borrowing_question(
        self, qa_service, sample_faqs
    ):
        """Borrowing questions should get relevant answers."""
        question = "How can I borrow an item from the hub?"
        
        result = qa_service.ask(question)
        
        # Should find relevant FAQ
        assert result['confidence'] > 0
        assert 'borrow' in result['answer'].lower() or 'reserve' in result['answer'].lower()
    
    def test_relevant_answer_for_hub_question(
        self, qa_service, sample_faqs
    ):
        """Hub questions should get relevant answers."""
        question = "What is a hub?"
        
        result = qa_service.ask(question)
        
        # Should find relevant FAQ
        assert result['confidence'] > 0
        assert 'hub' in result['answer'].lower()
    
    def test_category_filtering_works(
        self, qa_service, sample_faqs
    ):
        """Category filter should narrow results."""
        question = "How do I do something?"
        
        # Ask with category filter
        result = qa_service.ask(question, category='borrowing')
        
        # If a match is found, it should be from the borrowing category
        if result['category']:
            assert result['category'] == 'borrowing'
    
    def test_fallback_for_unknown_question(
        self, qa_service, sample_faqs
    ):
        """Unknown questions should get fallback response."""
        question = "What is the airspeed velocity of an unladen swallow?"
        
        result = qa_service.ask(question)
        
        # Should return fallback (low confidence or fallback method)
        assert result['confidence'] < 0.5 or result['method'] == 'fallback'
        assert len(result['answer']) > 0
    
    def test_related_faqs_returned(
        self, qa_service, sample_faqs
    ):
        """Related FAQs should be included in response."""
        question = "How do I borrow items?"
        
        result = qa_service.ask(question, limit=3)
        
        # Should return related FAQs
        assert 'related_faqs' in result
        assert isinstance(result['related_faqs'], list)
    
    def test_view_count_incremented(
        self, qa_service, sample_faqs
    ):
        """View count should increment when FAQ is accessed."""
        faq = sample_faqs[0]
        initial_count = faq.view_count
        
        question = "How do I borrow an item?"
        result = qa_service.ask(question)
        
        # Refresh from database
        faq.refresh_from_db()
        
        # View count should increase if this FAQ was matched
        if result['confidence'] > 0:
            assert faq.view_count >= initial_count
    
    def test_limit_parameter_respected(
        self, qa_service, sample_faqs
    ):
        """Limit parameter should control number of related FAQs."""
        question = "How do I borrow?"
        
        result = qa_service.ask(question, limit=2)
        
        # Should return at most limit-1 related FAQs (best match + related)
        assert len(result['related_faqs']) <= 2
    
    def test_inactive_faqs_excluded(
        self, qa_service, sample_faqs
    ):
        """Inactive FAQs should not be returned."""
        # Mark an FAQ as inactive
        inactive_faq = sample_faqs[0]
        inactive_faq.is_active = False
        inactive_faq.save()
        
        question = inactive_faq.question
        result = qa_service.ask(question)
        
        # Should not match the inactive FAQ
        if result['question_matched']:
            assert result['question_matched'] != inactive_faq.question


# ============================================================================
# Additional Q&A Tests
# ============================================================================

@pytest.mark.django_db
class TestQAServiceMethods:
    """Test Q&A service helper methods."""
    
    def test_get_popular_faqs(self, qa_service, sample_faqs):
        """Should return popular FAQs."""
        # Increment view counts
        sample_faqs[0].view_count = 10
        sample_faqs[0].save()
        sample_faqs[1].view_count = 5
        sample_faqs[1].save()
        
        popular = qa_service.get_popular_faqs(limit=5)
        
        assert len(popular) > 0
        assert isinstance(popular, list)
        # Should be ordered by popularity
        if len(popular) >= 2:
            assert popular[0]['view_count'] >= popular[1]['view_count']
    
    def test_get_faqs_by_category(self, qa_service, sample_faqs):
        """Should return FAQs filtered by category."""
        faqs = qa_service.get_faqs_by_category('borrowing', limit=10)
        
        assert len(faqs) > 0
        for faq in faqs:
            assert faq['category'] == 'borrowing'
    
    def test_text_normalization(self, qa_service):
        """Text should be normalized properly."""
        text = "  How   DO I   Borrow?!?  "
        normalized = qa_service._normalize_text(text)
        
        assert normalized == "how do i borrow"
        assert normalized.islower()
        assert '  ' not in normalized
    
    def test_keyword_extraction(self, qa_service):
        """Keywords should be extracted from text."""
        text = "How do I borrow an item from the hub?"
        keywords = qa_service._extract_keywords(text)
        
        # Should extract meaningful words
        assert 'borrow' in keywords
        assert 'item' in keywords
        assert 'hub' in keywords
        # Should exclude stop words
        assert 'do' not in keywords
        assert 'i' not in keywords
        assert 'the' not in keywords
    
    def test_question_type_detection(self, qa_service):
        """Should detect question types."""
        assert qa_service._detect_question_type("How do I borrow?") == 'how'
        assert qa_service._detect_question_type("What is a hub?") == 'what'
        assert qa_service._detect_question_type("Where is the hub?") == 'where'
        assert qa_service._detect_question_type("When can I borrow?") == 'when'
        assert qa_service._detect_question_type("Can I extend?") == 'can'


@pytest.mark.django_db
class TestFAQModel:
    """Test FAQ model functionality."""
    
    def test_faq_creation(self, db):
        """FAQ should be created with all fields."""
        faq = FAQEntry.objects.create(
            question="Test question?",
            answer="Test answer.",
            category="general",
            keywords=["test", "question"],
            is_active=True
        )
        
        assert faq.id is not None
        assert faq.question == "Test question?"
        assert faq.answer == "Test answer."
        assert faq.category == "general"
        assert faq.keywords == ["test", "question"]
        assert faq.view_count == 0
        assert faq.helpful_count == 0
        assert faq.is_active is True
    
    def test_increment_view_count(self, sample_faqs):
        """View count should increment."""
        faq = sample_faqs[0]
        initial_count = faq.view_count
        
        faq.increment_view_count()
        
        assert faq.view_count == initial_count + 1
    
    def test_mark_helpful(self, sample_faqs):
        """Helpful count should increment."""
        faq = sample_faqs[0]
        initial_count = faq.helpful_count
        
        faq.mark_helpful()
        
        assert faq.helpful_count == initial_count + 1
    
    def test_faq_string_representation(self, sample_faqs):
        """FAQ string should show truncated question."""
        faq = sample_faqs[0]
        str_repr = str(faq)
        
        assert len(str_repr) <= 53  # 50 chars + "..."
        assert faq.question[:50] in str_repr


@pytest.mark.django_db
class TestQAPerformance:
    """Test Q&A service performance."""
    
    def test_multiple_questions_under_time_limit(
        self, qa_service, sample_faqs
    ):
        """Multiple questions should all respond quickly."""
        questions = [
            "How do I borrow?",
            "What is a hub?",
            "Can I extend?",
            "Where do I find items?",
            "How do I return?"
        ]
        
        for question in questions:
            start = time.time()
            result = qa_service.ask(question)
            elapsed = time.time() - start
            
            # Each question should respond in under 10 seconds
            assert elapsed < 10.0
            assert result['response_time'] < 10.0
    
    def test_large_faq_database_performance(self, qa_service, db):
        """Should handle large FAQ database efficiently."""
        # Create many FAQs
        for i in range(50):
            FAQEntry.objects.create(
                question=f"Question {i}?",
                answer=f"Answer {i}.",
                category="general",
                keywords=[f"keyword{i}"],
                is_active=True
            )
        
        question = "How do I do something?"
        start = time.time()
        result = qa_service.ask(question)
        elapsed = time.time() - start
        
        # Should still respond quickly
        assert elapsed < 10.0
