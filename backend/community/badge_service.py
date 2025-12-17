"""
Badge Service - Ori notices, doesn't shout
Implements dignity-first gamification
"""
import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from community.models_gamification import Badge, UserBadge, UserLevel
from users.models import User
from users.models_notifications import Notification

logger = logging.getLogger(__name__)


class BadgeService:
    """
    Manages badge awards and progression
    Ori's voice: gentle, noticing, not aggressive
    """
    
    # Ori's gentle messages for badges
    ORI_MESSAGES = {
        'first-landing': "Ori noticed this is your beginning. Welcome home.",
        'settled-in': "You've found what you needed. That matters.",
        'found-my-flock': "Connections are forming. You're not alone here.",
        'warm-hands': "Someone will stay warm because of you.",
        'open-pantry': "You shared what nourishes. Thank you.",
        'tool-ally': "Tools in the right hands build better lives.",
        'reliable-wing': "Your consistency means others can count on you.",
        'welcomer': "You've made newcomers feel seen. That's everything.",
        'connector': "You brought people together. Community grows from this.",
        'community-builder': "You created space for others. This is leadership.",
        'steady-wing': "Stewards trust you. That trust was earned.",
        'hub-anchor': "This hub is stronger because you're here.",
    }
    
    @staticmethod
    def initialize_badges():
        """
        Create default badge definitions
        Called once during setup
        """
        badges = [
            # Arrival & Belonging
            {
                'name': 'First Landing',
                'slug': 'first-landing',
                'description': 'Completed first reservation',
                'category': 'arrival',
                'criteria': {'reservations_count': 1},
                'icon': '🪺',
                'color': '#10B981',
                'sort_order': 1
            },
            {
                'name': 'Settled In',
                'slug': 'settled-in',
                'description': 'Used 3 different essentials',
                'category': 'arrival',
                'criteria': {'unique_items_used': 3},
                'icon': '🏠',
                'color': '#3B82F6',
                'sort_order': 2
            },
            {
                'name': 'Found My Flock',
                'slug': 'found-my-flock',
                'description': 'Connected with 2 community members',
                'category': 'arrival',
                'criteria': {'connections_count': 2},
                'icon': '🤝',
                'color': '#8B5CF6',
                'sort_order': 3
            },
            
            # Contribution & Care
            {
                'name': 'Warm Hands',
                'slug': 'warm-hands',
                'description': 'Donated clothing',
                'category': 'contribution',
                'criteria': {'donated_clothing': True},
                'icon': '🧥',
                'color': '#EF4444',
                'sort_order': 4
            },
            {
                'name': 'Open Pantry',
                'slug': 'open-pantry',
                'description': 'Shared food items',
                'category': 'contribution',
                'criteria': {'donated_food': True},
                'icon': '🍲',
                'color': '#F59E0B',
                'sort_order': 5
            },
            {
                'name': 'Tool Ally',
                'slug': 'tool-ally',
                'description': 'Shared tools or equipment',
                'category': 'contribution',
                'criteria': {'donated_tools': True},
                'icon': '🔧',
                'color': '#6B7280',
                'sort_order': 6
            },
            {
                'name': 'Reliable Wing',
                'slug': 'reliable-wing',
                'description': 'Returned items on time consistently',
                'category': 'contribution',
                'criteria': {'on_time_returns': 10},
                'icon': '⏱️',
                'color': '#14B8A6',
                'sort_order': 7
            },
            
            # Community Energy
            {
                'name': 'Welcomer',
                'slug': 'welcomer',
                'description': 'Welcomed 5 newcomers',
                'category': 'community',
                'criteria': {'welcomed_newcomers': 5},
                'icon': '👋',
                'color': '#EC4899',
                'sort_order': 8
            },
            {
                'name': 'Connector',
                'slug': 'connector',
                'description': 'Introduced two people',
                'category': 'community',
                'criteria': {'introductions_made': 2},
                'icon': '🌉',
                'color': '#8B5CF6',
                'sort_order': 9
            },
            {
                'name': 'Community Builder',
                'slug': 'community-builder',
                'description': 'Hosted or supported an event',
                'category': 'community',
                'criteria': {'events_supported': 1},
                'icon': '🎪',
                'color': '#F59E0B',
                'sort_order': 10
            },
            
            # Steward & Trust
            {
                'name': 'Steady Wing',
                'slug': 'steady-wing',
                'description': 'Steward-approved reliable member',
                'category': 'trust',
                'criteria': {'steward_approved': True},
                'icon': '✨',
                'color': '#10B981',
                'sort_order': 11
            },
            {
                'name': 'Hub Anchor',
                'slug': 'hub-anchor',
                'description': 'Consistent support at a specific hub',
                'category': 'trust',
                'criteria': {'hub_visits': 20},
                'icon': '⚓',
                'color': '#3B82F6',
                'sort_order': 12
            },
        ]
        
        created_count = 0
        for badge_data in badges:
            _, created = Badge.objects.get_or_create(
                slug=badge_data['slug'],
                defaults=badge_data
            )
            if created:
                created_count += 1
        
        logger.info(f"Initialized {created_count} new badges")
        return created_count
    
    @staticmethod
    @transaction.atomic
    def award_badge(user: User, badge_slug: str, reason: Optional[str] = None) -> Optional[UserBadge]:
        """
        Award a badge to a user
        Ori notices and acknowledges, doesn't celebrate loudly
        """
        try:
            badge = Badge.objects.get(slug=badge_slug, is_active=True)
        except Badge.DoesNotExist:
            logger.warning(f"Badge {badge_slug} not found")
            return None
        
        # Check if user already has this badge
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            return None
        
        # Award the badge
        ori_message = reason or BadgeService.ORI_MESSAGES.get(badge_slug, "You earned this.")
        
        user_badge = UserBadge.objects.create(
            user=user,
            badge=badge,
            awarded_reason=ori_message
        )
        
        # Send gentle notification
        Notification.objects.create(
            recipient=user,
            notification_type='badge_earned',
            title=f"{badge.icon} {badge.name}",
            message=ori_message,
            data={
                'badge_id': str(badge.id),
                'badge_slug': badge.slug,
                'category': badge.category
            }
        )
        
        logger.info(f"Awarded badge '{badge.name}' to user {user.email}")
        return user_badge
    
    @staticmethod
    def check_user_for_badges(user: User) -> List[UserBadge]:
        """
        Check if user qualifies for any badges
        Returns list of newly awarded badges
        """
        from reservations.models import Reservation
        from inventory.models import InventoryItem
        
        newly_awarded = []
        
        # First Landing - completed first reservation
        if Reservation.objects.filter(user=user, status='completed').count() >= 1:
            badge = BadgeService.award_badge(user, 'first-landing')
            if badge:
                newly_awarded.append(badge)
        
        # Settled In - used 3 different items
        unique_items = Reservation.objects.filter(
            user=user,
            status='completed'
        ).values('item').distinct().count()
        
        if unique_items >= 3:
            badge = BadgeService.award_badge(user, 'settled-in')
            if badge:
                newly_awarded.append(badge)
        
        # Reliable Wing - 10 on-time returns
        on_time_returns = Reservation.objects.filter(
            user=user,
            status='completed',
            returned_at__lte=models.F('return_date')
        ).count()
        
        if on_time_returns >= 10:
            badge = BadgeService.award_badge(user, 'reliable-wing')
            if badge:
                newly_awarded.append(badge)
        
        # Warm Hands - donated clothing
        donated_clothing = InventoryItem.objects.filter(
            donor=user,
            category='Clothing'
        ).exists()
        
        if donated_clothing:
            badge = BadgeService.award_badge(user, 'warm-hands')
            if badge:
                newly_awarded.append(badge)
        
        # Hub Anchor - 20+ interactions at a hub
        if user.assigned_hub:
            hub_interactions = Reservation.objects.filter(
                user=user,
                item__hub=user.assigned_hub
            ).count()
            
            if hub_interactions >= 20:
                badge = BadgeService.award_badge(user, 'hub-anchor')
                if badge:
                    newly_awarded.append(badge)
        
        return newly_awarded
    
    @staticmethod
    def update_user_level(user: User):
        """
        Update user level based on activity
        Creates UserLevel if doesn't exist
        """
        user_level, created = UserLevel.objects.get_or_create(user=user)
        
        if created:
            logger.info(f"Created UserLevel for {user.email}")
        
        # Check for level up
        leveled_up = user_level.check_level_up()
        
        if leveled_up:
            # Send gentle Ori message
            Notification.objects.create(
                recipient=user,
                notification_type='level_up',
                title="You're growing with the flock",
                message=f"Ori noticed you've reached {user_level.get_current_level_display()}.",
                data={'level': user_level.current_level}
            )
            logger.info(f"User {user.email} leveled up to {user_level.current_level}")
        
        return user_level
    
    @staticmethod
    def get_user_badges(user: User) -> Dict:
        """
        Get user's badge collection
        Returns organized by category
        """
        user_badges = UserBadge.objects.filter(user=user).select_related('badge')
        
        badges_by_category = {
            'arrival': [],
            'contribution': [],
            'community': [],
            'trust': []
        }
        
        for ub in user_badges:
            badges_by_category[ub.badge.category].append({
                'id': str(ub.id),
                'name': ub.badge.name,
                'slug': ub.badge.slug,
                'icon': ub.badge.icon,
                'color': ub.badge.color,
                'description': ub.badge.description,
                'awarded_at': ub.awarded_at,
                'awarded_reason': ub.awarded_reason,
                'viewed': ub.viewed_at is not None
            })
        
        return {
            'badges': badges_by_category,
            'total_count': user_badges.count(),
            'unviewed_count': user_badges.filter(viewed_at__isnull=True).count()
        }


# Import models for badge checking
from django.db import models

# Singleton service
badge_service = BadgeService()
