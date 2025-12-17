"""
Mentorship matching service for connecting mentors with mentees.
Matches based on language, interests, location, and availability.
"""
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q, Count
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class MentorshipMatchingService:
    """Service for intelligent mentor-mentee matching."""
    
    @staticmethod
    def find_potential_mentors(mentee_user, max_results=10):
        """
        Find potential mentors for a mentee based on multiple criteria.
        
        Args:
            mentee_user: User seeking mentorship
            max_results: Maximum number of mentors to return
        
        Returns:
            List of matched mentor User objects with match scores
        """
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get all users marked as mentors who are not already connected
        potential_mentors = User.objects.filter(
            is_mentor=True,
            assigned_hub__isnull=False
        ).exclude(
            id=mentee_user.id
        ).exclude(
            mentoring__mentee=mentee_user,
            mentoring__status__in=['requested', 'active']
        )
        
        # Annotate with active mentorship count
        potential_mentors = potential_mentors.annotate(
            active_mentorships=Count(
                'mentoring',
                filter=Q(mentoring__status='active')
            )
        )
        
        # Filter out mentors with too many active mentorships (capacity check)
        max_mentorships = 5
        potential_mentors = potential_mentors.filter(
            active_mentorships__lt=max_mentorships
        )
        
        # Calculate match scores
        matched_mentors = []
        
        for mentor in potential_mentors[:max_results * 2]:  # Get extra for scoring
            score = MentorshipMatchingService._calculate_match_score(
                mentor, mentee_user
            )
            matched_mentors.append({
                'mentor': mentor,
                'score': score,
                'reasons': MentorshipMatchingService._get_match_reasons(
                    mentor, mentee_user, score
                )
            })
        
        # Sort by score descending
        matched_mentors.sort(key=lambda x: x['score'], reverse=True)
        
        return matched_mentors[:max_results]
    
    @staticmethod
    def _calculate_match_score(mentor, mentee):
        """
        Calculate match score between mentor and mentee.
        
        Scoring criteria:
        - Same hub: +30 points
        - Nearby hub (< 10km): +20 points
        - Same primary language: +25 points
        - Common interests: +5 points each (max 20)
        - Mentor experience level: +0-15 points
        - Mentee needs alignment: +0-10 points
        
        Returns:
            int: Match score (0-100)
        """
        score = 0
        
        # Hub proximity scoring
        if mentor.assigned_hub and mentee.assigned_hub:
            if mentor.assigned_hub == mentee.assigned_hub:
                score += 30
            elif mentor.assigned_hub.location and mentee.assigned_hub.location:
                # Calculate distance
                distance = mentor.assigned_hub.location.distance(
                    mentee.assigned_hub.location
                ) * 100  # Convert degrees to km (approximate)
                
                if distance < 10:  # Within 10km
                    score += 20
                elif distance < 25:  # Within 25km
                    score += 10
        
        # Language matching
        mentor_lang = mentor.preferred_language or 'en'
        mentee_lang = mentee.preferred_language or 'en'
        
        if mentor_lang == mentee_lang:
            score += 25
        
        # Interests matching
        mentor_interests = set(getattr(mentor, 'interests', []) or [])
        mentee_interests = set(getattr(mentee, 'interests', []) or [])
        
        common_interests = mentor_interests.intersection(mentee_interests)
        score += min(len(common_interests) * 5, 20)
        
        # Mentor experience (based on reputation and time in system)
        if mentor.reputation_score > 100:
            score += 15
        elif mentor.reputation_score > 50:
            score += 10
        elif mentor.reputation_score > 20:
            score += 5
        
        # Role alignment bonus
        if mentee.role == 'newcomer' and mentor.role in ['steward', 'community_member']:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    @staticmethod
    def _get_match_reasons(mentor, mentee, score):
        """
        Generate human-readable match reasons.
        
        Returns:
            List of reason strings
        """
        reasons = []
        
        if mentor.assigned_hub and mentee.assigned_hub:
            if mentor.assigned_hub == mentee.assigned_hub:
                reasons.append(f"Same hub: {mentor.assigned_hub.name}")
        
        mentor_lang = mentor.preferred_language or 'en'
        mentee_lang = mentee.preferred_language or 'en'
        
        if mentor_lang == mentee_lang:
            reasons.append(f"Speaks {mentor_lang}")
        
        mentor_interests = set(getattr(mentor, 'interests', []) or [])
        mentee_interests = set(getattr(mentee, 'interests', []) or [])
        common_interests = mentor_interests.intersection(mentee_interests)
        
        if common_interests:
            reasons.append(f"Shared interests: {', '.join(list(common_interests)[:3])}")
        
        if mentor.reputation_score > 50:
            reasons.append(f"Experienced member ({mentor.reputation_score} reputation)")
        
        return reasons
    
    @staticmethod
    def create_connection(mentor_id, mentee_id):
        """
        Create a new mentorship connection request.
        
        Returns:
            MentorshipConnection object
        """
        from community.models import MentorshipConnection
        from django.contrib.auth import get_user_model
        from users.notifications import NotificationService
        
        User = get_user_model()
        
        mentor = User.objects.get(id=mentor_id)
        mentee = User.objects.get(id=mentee_id)
        
        # Check if mentor is available
        if not mentor.is_mentor:
            raise ValueError("Selected user is not a mentor")
        
        # Check for existing connection
        existing = MentorshipConnection.objects.filter(
            mentor=mentor,
            mentee=mentee,
            status__in=['requested', 'active']
        ).first()
        
        if existing:
            raise ValueError("Mentorship connection already exists")
        
        # Create connection
        connection = MentorshipConnection.objects.create(
            mentor=mentor,
            mentee=mentee,
            status='requested'
        )
        
        # Notify mentor
        NotificationService.send_notification(
            user=mentor,
            notification_type='mentorship_request',
            title='New Mentorship Request',
            message=f"{mentee.get_full_name()} has requested you as a mentor",
            data={'connection_id': str(connection.id)}
        )
        
        logger.info(f"Mentorship connection requested: {mentor.email} <- {mentee.email}")
        
        return connection
    
    @staticmethod
    def accept_connection(connection_id, mentor_user):
        """
        Accept a mentorship connection request.
        
        Returns:
            Updated MentorshipConnection object
        """
        from community.models import MentorshipConnection
        from users.notifications import NotificationService
        from django.utils import timezone
        
        connection = MentorshipConnection.objects.get(id=connection_id)
        
        # Verify it's the mentor accepting
        if connection.mentor != mentor_user:
            raise ValueError("Only the mentor can accept this connection")
        
        if connection.status != 'requested':
            raise ValueError("Connection is not in requested status")
        
        # Update status
        connection.status = 'active'
        connection.start_date = timezone.now().date()
        connection.save()
        
        # Notify mentee
        NotificationService.send_notification(
            user=connection.mentee,
            notification_type='mentorship_accepted',
            title='Mentorship Request Accepted',
            message=f"{mentor_user.get_full_name()} has accepted your mentorship request",
            data={'connection_id': str(connection.id)}
        )
        
        logger.info(f"Mentorship connection accepted: {connection.id}")
        
        return connection
    
    @staticmethod
    def decline_connection(connection_id, mentor_user):
        """
        Decline a mentorship connection request.
        
        Returns:
            Updated MentorshipConnection object
        """
        from community.models import MentorshipConnection
        from users.notifications import NotificationService
        
        connection = MentorshipConnection.objects.get(id=connection_id)
        
        # Verify it's the mentor declining
        if connection.mentor != mentor_user:
            raise ValueError("Only the mentor can decline this connection")
        
        if connection.status != 'requested':
            raise ValueError("Connection is not in requested status")
        
        # Update status
        connection.status = 'declined'
        connection.save()
        
        # Notify mentee (gently)
        NotificationService.send_notification(
            user=connection.mentee,
            notification_type='mentorship_declined',
            title='Mentorship Request Update',
            message=f"{mentor_user.get_full_name()} is unable to mentor at this time. Try another match!",
            data={'connection_id': str(connection.id)}
        )
        
        logger.info(f"Mentorship connection declined: {connection.id}")
        
        return connection
