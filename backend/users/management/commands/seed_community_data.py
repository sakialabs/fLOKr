"""
Management command to seed community-related test data (users, badges, mentorships).
"""
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from community.models import Badge, UserBadge, MentorshipConnection


class Command(BaseCommand):
    help = 'Seeds community test data including users, badges, and mentorships'

    def handle(self, *args, **kwargs):
        """Main entry point for the management command."""
        self.stdout.write("=" * 60)
        self.stdout.write("Starting Community Data Seeding")
        self.stdout.write("=" * 60)
        
        try:
            self.create_test_users()
            self.create_badges()
            self.assign_badges()
            self.create_mentorships()
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS('✅ Seeding completed successfully!'))
            self.stdout.write("=" * 60)
            self.stdout.write("\nYou can now:")
            self.stdout.write("  • View profiles with real badges and contributions")
            self.stdout.write("  • See actual community highlights in leaderboard")
            self.stdout.write("  • Message real users in the sidebar")
            self.stdout.write("=" * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error during seeding: {str(e)}"))
            import traceback
            traceback.print_exc()

    def create_test_users(self):
        """Create test users with varied profiles."""
        self.stdout.write('\nCreating test users...')
        
        users_data = [
            {
                'username': 'sarah_m',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Martinez',
                'bio': 'Experienced community organizer passionate about sustainable living and tool sharing.',
                'skills': 'gardening,woodworking,community organizing',
                'languages_spoken': 'en,es',
                'is_mentor': True,
                'reputation_score': 450
            },
            {
                'username': 'michael_c',
                'email': 'michael@example.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'bio': 'DIY enthusiast and electronics tinkerer. Always happy to help with tech repairs!',
                'skills': 'electronics,programming,3d printing',
                'languages_spoken': 'en,zh',
                'is_mentor': True,
                'reputation_score': 380
            },
            {
                'username': 'emma_w',
                'email': 'emma@example.com',
                'first_name': 'Emma',
                'last_name': 'Williams',
                'bio': 'Sustainability advocate and skilled seamstress. Love teaching others!',
                'skills': 'sewing,upcycling,teaching',
                'languages_spoken': 'en,fr',
                'is_mentor': True,
                'reputation_score': 420
            },
            {
                'username': 'james_b',
                'email': 'james@example.com',
                'first_name': 'James',
                'last_name': 'Brown',
                'bio': 'New to the community and eager to learn sustainable living practices.',
                'skills': 'photography,cooking',
                'languages_spoken': 'en',
                'is_mentor': False,
                'reputation_score': 120
            },
            {
                'username': 'priya_s',
                'email': 'priya@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'bio': 'Urban gardener and composting expert. Building a greener city one plant at a time!',
                'skills': 'gardening,composting,urban farming',
                'languages_spoken': 'en,hi',
                'is_mentor': True,
                'reputation_score': 390
            },
            {
                'username': 'carlos_r',
                'email': 'carlos@example.com',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'bio': 'Carpenter and furniture restorer. Love giving old things new life!',
                'skills': 'carpentry,furniture restoration,tool repair',
                'languages_spoken': 'en,es',
                'is_mentor': True,
                'reputation_score': 410
            },
            {
                'username': 'aisha_k',
                'email': 'aisha@example.com',
                'first_name': 'Aisha',
                'last_name': 'Khan',
                'bio': 'Community advocate focused on accessibility and inclusion in sharing economy.',
                'skills': 'community organizing,event planning',
                'languages_spoken': 'en,ur',
                'is_mentor': False,
                'reputation_score': 200
            },
            {
                'username': 'david_l',
                'email': 'david@example.com',
                'first_name': 'David',
                'last_name': 'Lee',
                'bio': 'Recently joined to borrow tools for home improvement projects.',
                'skills': 'home repair,painting',
                'languages_spoken': 'en',
                'is_mentor': False,
                'reputation_score': 80
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'bio': user_data['bio'],
                    'skills': user_data['skills'],
                    'languages_spoken': user_data['languages_spoken'],
                    'is_mentor': user_data['is_mentor'],
                    'reputation_score': user_data['reputation_score']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f"  ✓ Created user: {user.get_full_name()}")
            else:
                # Update existing user
                for key, value in user_data.items():
                    if key not in ['username', 'email']:
                        setattr(user, key, value)
                user.save()
                self.stdout.write(f"  ✓ Updated user: {user.get_full_name()}")
            created_users.append(user)
        
        return created_users

    def create_badges(self):
        """Create standard badges."""
        self.stdout.write('\nCreating badges...')
        
        badges_data = [
            {
                'name': 'Reliable Returner',
                'description': 'Consistently returns items on time',
                'icon': '🎯',
                'criteria': 'Return 5+ items on time'
            },
            {
                'name': 'Generous Donor',
                'description': 'Contributed valuable items to the community',
                'icon': '💝',
                'criteria': 'Donate 3+ items'
            },
            {
                'name': 'Community Helper',
                'description': 'Actively helps others in the community',
                'icon': '🤝',
                'criteria': 'Complete 10+ successful rentals'
            },
            {
                'name': 'Newcomer Champion',
                'description': 'Welcomes and helps new community members',
                'icon': '🌟',
                'criteria': 'Help 3+ new members get started'
            },
            {
                'name': 'Super Mentor',
                'description': 'Dedicated to mentoring community members',
                'icon': '🦉',
                'criteria': 'Mentor 3+ community members'
            },
            {
                'name': 'Positive Impact',
                'description': 'Makes the community better for everyone',
                'icon': '✨',
                'criteria': 'Maintain 4.5+ star rating over 20+ interactions'
            }
        ]
        
        created_badges = []
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults={
                    'description': badge_data['description'],
                    'icon': badge_data['icon'],
                    'criteria': badge_data['criteria']
                }
            )
            if created:
                self.stdout.write(f"  ✓ Created badge: {badge.icon} {badge.name}")
            created_badges.append(badge)
        
        return created_badges

    def assign_badges(self):
        """Assign badges to users."""
        self.stdout.write('\nAssigning badges to users...')
        
        users = list(User.objects.all()[:8])
        badges = list(Badge.objects.all())
        
        # Map badge names to badge objects
        badge_dict = {badge.name: badge for badge in badges}
        
        # Assignments: (user first_name, [badge_names])
        assignments = [
            ('Sarah', ['Reliable Returner', 'Community Helper', 'Super Mentor']),
            ('Michael', ['Reliable Returner', 'Generous Donor', 'Positive Impact']),
            ('Emma', ['Community Helper', 'Super Mentor', 'Positive Impact']),
            ('James', ['Newcomer Champion', 'Reliable Returner']),
            ('Priya', ['Generous Donor', 'Community Helper', 'Positive Impact']),
            ('Carlos', ['Reliable Returner', 'Generous Donor', 'Community Helper']),
            ('Aisha', ['Newcomer Champion', 'Community Helper']),
            ('David', ['Reliable Returner']),
        ]
        
        for first_name, badge_names in assignments:
            user = next((u for u in users if u.first_name == first_name), None)
            if not user:
                continue
                
            for badge_name in badge_names:
                badge = badge_dict.get(badge_name)
                if badge:
                    # Award badges at different times for realistic feed
                    days_ago = 5 + len(badge_names) * 2
                    user_badge, created = UserBadge.objects.get_or_create(
                        user=user,
                        badge=badge,
                        defaults={
                            'awarded_at': timezone.now() - timedelta(days=days_ago),
                            'awarded_reason': f'Earned through community contributions'
                        }
                    )
                    if created:
                        self.stdout.write(f"  ✓ Awarded {badge.icon} {badge.name} to {user.first_name}")

    def create_mentorships(self):
        """Create mentorship connections."""
        self.stdout.write('\nCreating mentorship connections...')
        
        users = list(User.objects.all()[:8])
        mentors = [u for u in users if u.is_mentor]
        mentees = [u for u in users if not u.is_mentor]
        
        if len(mentors) < 3 or len(mentees) < 2:
            self.stdout.write(self.style.WARNING('  Not enough users to create mentorships'))
            return
            
        connections = [
            (mentors[0], mentees[0]),  # Sarah mentors James
            (mentors[1], mentees[1]),  # Michael mentors David
            (mentors[2], mentees[0]),  # Emma also mentors James
        ]
        
        for mentor, mentee in connections:
            connection, created = MentorshipConnection.objects.get_or_create(
                mentor=mentor,
                mentee=mentee,
                defaults={
                    'status': 'active',
                    'start_date': (timezone.now() - timedelta(days=15)).date()
                }
            )
            if created:
                self.stdout.write(f"  ✓ Connected {mentor.first_name} (mentor) with {mentee.first_name} (mentee)")
