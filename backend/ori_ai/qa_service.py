"""
Ori AI - Natural Language Q&A Service

Provides intelligent question answering using:
- Semantic search with sentence transformers
- FAQ knowledge base
- Fallback responses for unknown questions
- Response time optimization (<10 seconds)
"""

from typing import List, Dict, Any, Optional
from django.db.models import Q
import re
import time


class QAService:
    """
    Natural language question answering service.
    Uses semantic similarity and keyword matching for FAQ retrieval.
    """
    
    # Common question patterns
    QUESTION_PATTERNS = {
        'how': r'\bhow\b',
        'what': r'\bwhat\b',
        'when': r'\bwhen\b',
        'where': r'\bwhere\b',
        'why': r'\bwhy\b',
        'who': r'\bwho\b',
        'can': r'\bcan\s+i\b',
        'do': r'\bdo\s+i\b',
    }
    
    # Fallback responses for unknown questions
    FALLBACK_RESPONSES = [
        "I'm not sure about that specific question, but I can help you with borrowing items, finding hubs, or connecting with mentors. What would you like to know?",
        "That's a great question! While I don't have a specific answer, you can contact your hub steward for personalized assistance.",
        "I don't have information on that topic yet, but I'm learning! Try asking about reservations, inventory, or community features.",
    ]
    
    def __init__(self):
        """Initialize the Q&A service."""
        self.use_transformers = self._check_transformers_available()
        if self.use_transformers:
            self._initialize_model()
    
    def _check_transformers_available(self) -> bool:
        """Check if sentence transformers library is available."""
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model for fast inference
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_cache = {}
        except Exception as e:
            print(f"Warning: Could not initialize sentence transformer: {e}")
            self.use_transformers = False
    
    def ask(
        self,
        question: str,
        category: Optional[str] = None,
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Answer a natural language question.
        
        Args:
            question: The user's question
            category: Optional category filter
            limit: Maximum number of FAQ results to return
            
        Returns:
            Dictionary with answer, confidence, and related FAQs
        """
        start_time = time.time()
        
        from ori_ai.models import FAQEntry
        
        # Normalize question
        question_normalized = self._normalize_text(question)
        
        # Get active FAQs
        faqs = FAQEntry.objects.filter(is_active=True)
        if category:
            faqs = faqs.filter(category=category)
        
        # Find best matches
        if self.use_transformers:
            matches = self._semantic_search(question_normalized, faqs, limit)
        else:
            matches = self._keyword_search(question_normalized, faqs, limit)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Build response
        if matches:
            best_match = matches[0]
            
            # Increment view count for best match
            best_match['faq'].increment_view_count()
            
            return {
                'answer': best_match['faq'].answer,
                'confidence': best_match['score'],
                'question_matched': best_match['faq'].question,
                'category': best_match['faq'].category,
                'related_faqs': [
                    {
                        'question': m['faq'].question,
                        'answer': m['faq'].answer,
                        'category': m['faq'].category,
                        'score': m['score']
                    }
                    for m in matches[1:limit]
                ],
                'response_time': response_time,
                'method': 'semantic' if self.use_transformers else 'keyword'
            }
        else:
            # No matches found - return fallback
            return {
                'answer': self._get_fallback_response(question_normalized),
                'confidence': 0.0,
                'question_matched': None,
                'category': None,
                'related_faqs': [],
                'response_time': response_time,
                'method': 'fallback'
            }
    
    def _semantic_search(
        self,
        question: str,
        faqs,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using sentence transformers.
        
        Args:
            question: Normalized question text
            faqs: QuerySet of FAQ entries
            limit: Maximum results
            
        Returns:
            List of matches with scores
        """
        from sentence_transformers import util
        
        # Encode question
        question_embedding = self.model.encode(question, convert_to_tensor=True)
        
        # Score all FAQs
        matches = []
        for faq in faqs:
            # Get or compute FAQ embedding
            faq_key = str(faq.id)
            if faq_key not in self.embeddings_cache:
                faq_text = f"{faq.question} {' '.join(faq.keywords)}"
                self.embeddings_cache[faq_key] = self.model.encode(
                    faq_text,
                    convert_to_tensor=True
                )
            
            # Calculate similarity
            similarity = util.cos_sim(
                question_embedding,
                self.embeddings_cache[faq_key]
            ).item()
            
            matches.append({
                'faq': faq,
                'score': similarity
            })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter by minimum threshold (0.3 = 30% similarity)
        matches = [m for m in matches if m['score'] >= 0.3]
        
        return matches[:limit]
    
    def _keyword_search(
        self,
        question: str,
        faqs,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search (fallback when transformers unavailable).
        
        Args:
            question: Normalized question text
            faqs: QuerySet of FAQ entries
            limit: Maximum results
            
        Returns:
            List of matches with scores
        """
        # Extract keywords from question
        keywords = self._extract_keywords(question)
        
        if not keywords:
            return []
        
        # Score FAQs by keyword overlap
        matches = []
        for faq in faqs:
            score = self._calculate_keyword_score(keywords, faq)
            if score > 0:
                matches.append({
                    'faq': faq,
                    'score': score
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:limit]
    
    def _calculate_keyword_score(self, keywords: List[str], faq) -> float:
        """Calculate keyword match score for an FAQ."""
        faq_text = f"{faq.question} {faq.answer} {' '.join(faq.keywords)}".lower()
        
        score = 0.0
        for keyword in keywords:
            if keyword in faq_text:
                # Weight by keyword importance
                if keyword in faq.question.lower():
                    score += 2.0  # Question match is most important
                elif keyword in faq.keywords:
                    score += 1.5  # Keyword match
                else:
                    score += 1.0  # Answer match
        
        # Normalize by number of keywords
        if keywords:
            score = score / len(keywords)
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common stop words
        stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'i', 'you', 'we',
            'they', 'he', 'she', 'it', 'this', 'that', 'these', 'those',
            'from'
        }
        
        # Normalize text first (removes punctuation)
        text = self._normalize_text(text)
        
        # Split and filter
        words = text.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters including question marks
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _get_fallback_response(self, question: str) -> str:
        """Get appropriate fallback response."""
        # Detect question type
        question_type = self._detect_question_type(question)
        
        # Return contextual fallback
        if question_type == 'how':
            return "I don't have specific instructions for that, but you can find help in our FAQ section or contact your hub steward for guidance."
        elif question_type == 'where':
            return "For location-specific questions, please check the Hubs section or contact your assigned hub steward."
        elif question_type == 'when':
            return "For timing and schedule questions, please refer to your hub's operating hours or contact your steward."
        else:
            # Default fallback
            return self.FALLBACK_RESPONSES[0]
    
    def _detect_question_type(self, question: str) -> Optional[str]:
        """Detect the type of question being asked."""
        for q_type, pattern in self.QUESTION_PATTERNS.items():
            if re.search(pattern, question, re.IGNORECASE):
                return q_type
        return None
    
    def get_popular_faqs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular/helpful FAQs.
        
        Args:
            limit: Maximum number of FAQs
            
        Returns:
            List of popular FAQs
        """
        from ori_ai.models import FAQEntry
        
        faqs = FAQEntry.objects.filter(is_active=True)[:limit]
        
        return [
            {
                'id': str(faq.id),
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category,
                'view_count': faq.view_count,
                'helpful_count': faq.helpful_count
            }
            for faq in faqs
        ]
    
    def get_faqs_by_category(
        self,
        category: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get FAQs filtered by category.
        
        Args:
            category: Category to filter by
            limit: Maximum number of FAQs
            
        Returns:
            List of FAQs in category
        """
        from ori_ai.models import FAQEntry
        
        faqs = FAQEntry.objects.filter(
            is_active=True,
            category=category
        )[:limit]
        
        return [
            {
                'id': str(faq.id),
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category
            }
            for faq in faqs
        ]


# Global instance
qa_service = QAService()
