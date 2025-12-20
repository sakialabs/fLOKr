"""
Message service for in-app messaging with translation support.
Enables cross-language communication between mentors and mentees.
"""
from django.utils import timezone
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Service for managing messages with translation support."""
    
    @staticmethod
    def create_message(connection, sender, content):
        """
        Create a new message in a mentorship connection.
        
        Args:
            connection: MentorshipConnection instance
            sender: User sending the message
            content: Message content string
        
        Returns:
            Message instance
        """
        from .models import Message
        
        # Verify sender is part of the connection
        if sender not in [connection.mentor, connection.mentee]:
            raise ValueError("Sender is not part of this connection")
        
        # Create message
        message = Message.objects.create(
            connection=connection,
            sender=sender,
            content=content
        )
        
        # Auto-translate if recipient uses different language
        MessageService.auto_translate_message(message)
        
        # Send notification to recipient
        MessageService._notify_recipient(message)
        
        return message
    
    @staticmethod
    def auto_translate_message(message):
        """
        Automatically translate message if sender and recipient use different languages.
        Stores translations in translated_content JSON field.
        
        Args:
            message: Message instance
        """
        from ori_ai.translation_service import TranslationService
        
        connection = message.connection
        sender = message.sender
        
        # Determine recipient
        recipient = connection.mentee if sender == connection.mentor else connection.mentor
        
        # Get languages
        sender_lang = sender.preferred_language or 'en'
        recipient_lang = recipient.preferred_language or 'en'
        
        # Skip if same language
        if sender_lang == recipient_lang:
            return
        
        try:
            # Translate to recipient's language
            translated = TranslationService.translate(
                text=message.content,
                source_lang=sender_lang,
                target_lang=recipient_lang
            )
            
            # Store translation
            message.translated_content = {
                recipient_lang: translated,
                'original_lang': sender_lang
            }
            message.save(update_fields=['translated_content'])
            
            logger.info(
                f"Translated message {message.id} from {sender_lang} to {recipient_lang}"
            )
        
        except Exception as e:
            logger.error(f"Translation failed for message {message.id}: {str(e)}")
            # Continue without translation - not critical
    
    @staticmethod
    def get_translated_content(message, user_language):
        """
        Get message content in user's preferred language.
        
        Args:
            message: Message instance
            user_language: Preferred language code
        
        Returns:
            str: Translated content or original if translation not available
        """
        # If no translation needed, return original
        if not message.translated_content:
            return message.content
        
        # Return translated version if available
        if user_language in message.translated_content:
            return message.translated_content[user_language]
        
        # Fallback to original
        return message.content
    
    @staticmethod
    def get_conversation_history(connection, requesting_user, limit=50):
        """
        Get conversation history with auto-translated content.
        
        Args:
            connection: MentorshipConnection instance
            requesting_user: User requesting the history
            limit: Maximum number of messages to return
        
        Returns:
            List of message dictionaries with translated content
        """
        from .models import Message
        
        # Get messages
        messages = Message.objects.filter(
            connection=connection
        ).select_related('sender').order_by('-created_at')[:limit]
        
        # Reverse to chronological order
        messages = list(reversed(messages))
        
        # Format with translations
        user_lang = requesting_user.preferred_language or 'en'
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': str(msg.id),
                'sender_id': str(msg.sender.id),
                'sender_name': msg.sender.get_full_name(),
                'content': MessageService.get_translated_content(msg, user_lang),
                'original_content': msg.content,
                'is_translated': user_lang in (msg.translated_content or {}),
                'read': msg.read,
                'created_at': msg.created_at.isoformat()
            })
        
        return formatted_messages
    
    @staticmethod
    def mark_messages_read(connection, user):
        """
        Mark all messages from the other person as read.
        
        Args:
            connection: MentorshipConnection instance
            user: User marking messages as read
        """
        from .models import Message
        
        # Get messages sent by the other person
        Message.objects.filter(
            connection=connection
        ).exclude(
            sender=user
        ).update(read=True)
    
    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread messages for a user.
        
        Args:
            user: User instance
        
        Returns:
            int: Count of unread messages
        """
        from .models import Message
        from django.db.models import Q
        
        # Count unread messages in connections where user is involved
        unread = Message.objects.filter(
            Q(connection__mentor=user) | Q(connection__mentee=user)
        ).exclude(
            sender=user
        ).filter(
            read=False
        ).count()
        
        return unread
    
    @staticmethod
    def _notify_recipient(message):
        """
        Send notification to message recipient.
        
        Args:
            message: Message instance
        """
        from users.notifications import NotificationService
        
        connection = message.connection
        sender = message.sender
        
        # Determine recipient
        recipient = connection.mentee if sender == connection.mentor else connection.mentor
        
        # Get translated content for recipient
        recipient_lang = recipient.preferred_language or 'en'
        content = MessageService.get_translated_content(message, recipient_lang)
        
        # Truncate content for notification
        preview = content[:100] + '...' if len(content) > 100 else content
        
        # Send notification
        NotificationService.send_notification(
            user=recipient,
            notification_type='message',
            title=f'New message from {sender.get_full_name()}',
            message=preview,
            data={
                'connection_id': str(connection.id),
                'message_id': str(message.id),
                'sender_id': str(sender.id)
            }
        )
    
    @staticmethod
    def delete_message(message, requesting_user):
        """
        Delete a message (only sender can delete their own messages).
        
        Args:
            message: Message instance
            requesting_user: User requesting deletion
        
        Returns:
            bool: Success status
        """
        if message.sender != requesting_user:
            raise ValueError("You can only delete your own messages")
        
        message.delete()
        return True
    
    @staticmethod
    def get_connection_summary(connection):
        """
        Get summary of a mentorship connection including message stats.
        
        Args:
            connection: MentorshipConnection instance
        
        Returns:
            Dict with connection summary
        """
        from .models import Message
        
        total_messages = connection.messages.count()
        unread_messages = connection.messages.filter(read=False).count()
        last_message = connection.messages.order_by('-created_at').first()
        
        return {
            'connection_id': str(connection.id),
            'mentor_id': str(connection.mentor.id),
            'mentor_name': connection.mentor.get_full_name(),
            'mentee_id': str(connection.mentee.id),
            'mentee_name': connection.mentee.get_full_name(),
            'status': connection.status,
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'last_message_at': last_message.created_at if last_message else None,
            'last_message_preview': last_message.content[:50] if last_message else None
        }
