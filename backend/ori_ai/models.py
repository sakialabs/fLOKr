from django.db import models
import uuid


class FAQEntry(models.Model):
    """
    FAQ knowledge base entry for natural language Q&A.
    Stores questions, answers, and metadata for semantic search.
    """
    
    class Category(models.TextChoices):
        GENERAL = 'general', 'General'
        BORROWING = 'borrowing', 'Borrowing & Reservations'
        INVENTORY = 'inventory', 'Inventory & Items'
        HUBS = 'hubs', 'Hubs & Locations'
        MENTORSHIP = 'mentorship', 'Mentorship'
        COMMUNITY = 'community', 'Community & Badges'
        ACCOUNT = 'account', 'Account & Profile'
        TECHNICAL = 'technical', 'Technical Support'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(help_text="The question text")
    answer = models.TextField(help_text="The answer text")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )
    keywords = models.JSONField(
        default=list,
        help_text="Keywords for search optimization"
    )
    view_count = models.IntegerField(default=0, help_text="Number of times viewed")
    helpful_count = models.IntegerField(default=0, help_text="Number of helpful votes")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ori_ai_faq'
        ordering = ['-helpful_count', '-view_count']
        verbose_name = 'FAQ Entry'
        verbose_name_plural = 'FAQ Entries'
    
    def __str__(self):
        return f"{self.question[:50]}..."
    
    def increment_view_count(self):
        """Increment view count when FAQ is accessed."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def mark_helpful(self):
        """Mark this FAQ as helpful."""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])
