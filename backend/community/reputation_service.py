"""
Dignity-first reputation tracking service.
No public rankings, only private scores and optional community celebration.
"""
from django.contrib.auth import get_user_model
from django.db.models import F
import random

User = get_user_model()


class ReputationService:
    """Service for managing user reputation in a dignity-first way."""
    
    # Reputation point awards for positive actions
    POINTS = {
        'on_time_return': 5,
        'help_newcomer': 10,
        'donate_item': 8,
        'positive_feedback': 3,
        'mentor_connection': 15,
        'event_participation': 7,
        'consecutive_returns': 5,  # After 5 consecutive on-time returns
    }
    
    # Ori's gentle acknowledgment messages (rotated randomly)
    ORI_ACKNOWLEDGMENTS = {
        'on_time_return': [
            "Ori noticed you returned everything on time. Thank you.",
            "Your reliability helps everyone. Ori appreciates it.",
            "Returning on time makes the flock stronger.",
        ],
        'help_newcomer': [
            "Ori noticed you've been welcoming lately. That matters.",
            "Helping someone land well—Ori sees that.",
            "You made someone's arrival easier. Thank you.",
        ],
        'donate_item': [
            "Ori noticed your contribution. Someone will benefit from this.",
            "Sharing what you have—that's flock energy.",
            "Your donation matters. Thank you.",
        ],
        'positive_feedback': [
            "Ori noticed positive feedback about you.",
            "Your care is noticed. Thank you.",
        ],
        'mentor_connection': [
            "Ori thinks mentorship is a beautiful thing.",
            "Guiding someone—that's powerful. Thank you.",
        ],
        'milestone_50': [
            "Ori noticed you've helped a lot lately. Thank you.",
            "You've been a steady presence here.",
        ],
        'milestone_100': [
            "Ori sees how much you contribute. That's meaningful.",
            "You've built real trust here. Thank you.",
        ],
    }
    
    @staticmethod
    def award_points(user, action_type, reason=None):
        """
        Award reputation points for positive actions.
        Private score only - no public rankings.
        
        Args:
            user: User instance
            action_type: Type of action (key from POINTS dict)
            reason: Optional specific reason for the award
        """
        if action_type not in ReputationService.POINTS:
            return
        
        points = ReputationService.POINTS[action_type]
        old_score = user.reputation_score
        
        # Update reputation score
        User.objects.filter(pk=user.pk).update(
            reputation_score=F('reputation_score') + points
        )
        user.refresh_from_db()
        
        # Send Ori's gentle acknowledgment (not always, just sometimes)
        if random.random() < 0.3:  # 30% chance to send acknowledgment
            ReputationService._send_ori_acknowledgment(user, action_type, points)
        
        # Check for milestone acknowledgments
        ReputationService._check_milestones(user, old_score, user.reputation_score)
    
    @staticmethod
    def _send_ori_acknowledgment(user, action_type, points):
        """Send a gentle acknowledgment from Ori (not every time)."""
        if action_type in ReputationService.ORI_ACKNOWLEDGMENTS:
            messages = ReputationService.ORI_ACKNOWLEDGMENTS[action_type]
            message = random.choice(messages)
            
            send_notification(
                user=user,
                notification_type='ori_acknowledgment',
                title="A word from Ori",
                message=message,
                data={'action': action_type, 'points': points}
            )
    
    @staticmethod
    def _check_milestones(user, old_score, new_score):
        """Check if user crossed a milestone threshold."""
        milestones = [50, 100, 200, 500]
        
        for milestone in milestones:
            if old_score < milestone <= new_score:
                key = f'milestone_{milestone}'
                if key in ReputationService.ORI_ACKNOWLEDGMENTS:
                    messages = ReputationService.ORI_ACKNOWLEDGMENTS[key]
                    message = random.choice(messages)
                    
                    send_notification(
                        user=user,
                        notification_type='milestone',
                        title="Ori noticed",
                        message=message,
                        data={'milestone': milestone, 'reputation': new_score}
                    )
                    break  # Only send one milestone message
    
    @staticmethod
    def get_community_highlights(limit=10):
        """
        Get optional community highlights - celebrates contributors without ranking.
        This is NOT a leaderboard - no numbers, no rankings, just gentle celebration.
        
        Returns users who have been particularly helpful recently.
        """
        # Get active contributors (reputation > 30) who have been active in last 30 days
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Get users with recent positive actions (via reservation returns, donations, etc)
        from reservations.models import Reservation
        from inventory.models import InventoryItem
        
        # Users with recent on-time returns
        recent_returners = User.objects.filter(
            reservations__status='completed',
            reservations__actual_return_date__gte=thirty_days_ago.date()
        ).distinct()
        
        # Users who donated recently
        recent_donors = User.objects.filter(
            donated_items__created_at__gte=thirty_days_ago
        ).distinct()
        
        # Combine and get users with reputation > 30
        highlighted_users = (recent_returners | recent_donors).filter(
            reputation_score__gte=30
        ).order_by('?')[:limit]  # Random order - no ranking
        
        return [{
            'id': str(user.id),
            'name': user.get_full_name(),
            'gentle_note': ReputationService._get_gentle_note(user)
        } for user in highlighted_users]
    
    @staticmethod
    def _get_gentle_note(user):
        """Get a gentle note about a user's contributions (no specific numbers)."""
        notes = [
            "has been helping lately",
            "has been reliable",
            "has been welcoming",
            "has been sharing",
            "has been a steady presence",
            "has been supporting the community",
        ]
        return random.choice(notes)
    
    @staticmethod
    def get_personal_reputation_summary(user):
        """
        Get a user's personal reputation summary.
        This is private - only the user sees their own score.
        """
        return {
            'reputation_score': user.reputation_score,
            'level': user.current_level,
            'ori_message': ReputationService._get_personal_ori_message(user),
            'recent_acknowledgments': []  # TODO: Track recent acknowledgments if needed
        }
    
    @staticmethod
    def _get_personal_ori_message(user):
        """Get a personalized message from Ori about their progress."""
        score = user.reputation_score
        
        if score < 20:
            return "You're just getting started. Welcome."
        elif score < 50:
            return "You're finding your rhythm here."
        elif score < 100:
            return "You've become part of the flock."
        elif score < 200:
            return "You're a trusted wing here."
        else:
            return "You've built something meaningful here. Thank you."
