"""
Management command to seed the database with realistic development data using Faker.
This replaces all mock data with believable, interconnected data for a real user experience.
"""
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta, datetime, date
from decimal import Decimal
import random

from faker import Faker

from users.models import User
from hubs.models import Hub, Event, Announcement
from inventory.models import InventoryItem
from reservations.models import Reservation
from community.models import Badge, UserBadge, Feedback, MentorshipConnection, Message


class Command(BaseCommand):
    help = 'Seeds the database with realistic development data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        fake = Faker(['en_CA', 'en_US'])
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()
        
        self.stdout.write(self.style.SUCCESS('Starting realistic data seeding...'))
        
        # Create data in proper order (respecting foreign keys)
        hubs = self._create_hubs(fake)
        users = self._create_users(fake, hubs)
        items = self._create_inventory_items(fake, hubs, users)
        reservations = self._create_reservations(fake, users, items, hubs)
        badges = self._create_badges()
        self._create_user_badges(users, badges)
        self._create_mentorship_connections(fake, users)
        self._create_events(fake, hubs, users)
        self._create_announcements(fake, hubs, users)
        self._create_feedback(fake, users, items, reservations)
        
        self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully with realistic data'))

    def _clear_data(self):
        """Clear all data from relevant tables"""
        Message.objects.all().delete()
        MentorshipConnection.objects.all().delete()
        UserBadge.objects.all().delete()
        Badge.objects.all().delete()
        Feedback.objects.all().delete()
        Reservation.objects.all().delete()
        InventoryItem.objects.all().delete()
        Event.objects.all().delete()
        Announcement.objects.all().delete()
        Hub.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('  Data cleared'))

    def _create_hubs(self, fake):
        """Create realistic community hubs"""
        self.stdout.write('Creating hubs...')
        
        hub_names = [
            "Eastside Community Hub",
            "Westdale Sharing Centre",
            "North Hamilton Resource Hub",
            "Downtown Commons",
            "Waterfront Community Space"
        ]
        
        # Hamilton, Ontario coordinates (approximate)
        base_lat, base_lon = 43.2557, -79.8711
        
        hubs = []
        for i, name in enumerate(hub_names):
            # Spread hubs around Hamilton area
            lat = base_lat + random.uniform(-0.05, 0.05)
            lon = base_lon + random.uniform(-0.05, 0.05)
            
            hub = Hub.objects.create(
                name=name,
                address=fake.street_address() + f", Hamilton, ON L{random.randint(8,9)}{random.choice(['P','R','S','T'])}{random.randint(1,9)}",
                location=Point(lon, lat),
                operating_hours={
                    'Monday': '9:00 AM - 7:00 PM',
                    'Tuesday': '9:00 AM - 7:00 PM',
                    'Wednesday': '9:00 AM - 7:00 PM',
                    'Thursday': '9:00 AM - 8:00 PM',
                    'Friday': '9:00 AM - 8:00 PM',
                    'Saturday': '10:00 AM - 5:00 PM',
                    'Sunday': 'Closed' if random.random() > 0.3 else '11:00 AM - 4:00 PM'
                },
                capacity=random.randint(80, 150),
                status='active'
            )
            hubs.append(hub)
            self.stdout.write(f'  ✓ {name}')
        
        return hubs

    def _create_users(self, fake, hubs):
        """Create diverse users with realistic profiles"""
        self.stdout.write('Creating users...')
        
        users = []
        
        # Distribution: 30% newcomers, 50% community members, 15% stewards, 5% partners
        roles_distribution = [
            ('newcomer', 15),
            ('community_member', 25),
            ('steward', 8),
            ('partner', 2)
        ]
        
        languages = ['en', 'es', 'ar', 'fr', 'zh', 'ur', 'so']
        
        for role, count in roles_distribution:
            for i in range(count):
                # Create realistic profiles
                first_name = fake.first_name()
                last_name = fake.last_name()
                
                # Newcomers joined more recently
                if role == 'newcomer':
                    days_ago = random.randint(1, 14)
                elif role == 'community_member':
                    days_ago = random.randint(30, 365)
                else:
                    days_ago = random.randint(180, 730)
                
                join_date = timezone.now() - timedelta(days=days_ago)
                
                # Generate phone number and ensure it's not longer than 20 characters
                phone_number = fake.phone_number() if random.random() > 0.3 else ''
                if len(phone_number) > 20:
                    phone_number = phone_number[:20]
                
                user = User.objects.create_user(
                    email=f"{first_name.lower()}.{last_name.lower()}{random.randint(1,99)}@example.com",
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    phone=phone_number,
                    preferred_language=random.choice(languages) if role == 'newcomer' else 'en',
                    address=fake.address(),
                    date_joined=join_date,
                    is_active=True
                )
                
                # Assign to a hub (community members and stewards)
                if role in ['community_member', 'steward', 'newcomer']:
                    user.assigned_hub = random.choice(hubs)
                    user.save()
                
                # Assign stewards to manage their hubs
                if role == 'steward' and user.assigned_hub:
                    user.assigned_hub.stewards.add(user)
                
                users.append(user)
        
        self.stdout.write(f'  ✓ Created {len(users)} users across all roles')
        return users

    def _create_inventory_items(self, fake, hubs, users):
        """Create diverse inventory items"""
        self.stdout.write('Creating inventory items...')
        
        categories_items = {
            'Household': ['Vacuum Cleaner', 'Iron', 'Blender', 'Toaster', 'Coffee Maker', 'Microwave', 'Space Heater', 'Fan'],
            'Tools': ['Drill', 'Hammer', 'Screwdriver Set', 'Ladder', 'Wrench Set', 'Power Saw', 'Level', 'Tape Measure'],
            'Winter Gear': ['Winter Coat', 'Boots', 'Gloves', 'Scarf', 'Hat', 'Snow Pants', 'Thermal Underwear'],
            'Kitchen': ['Pots & Pans Set', 'Dishes Set', 'Cutlery Set', 'Baking Sheets', 'Mixing Bowls', 'Food Storage Containers'],
            'Baby & Kids': ['Stroller', 'High Chair', 'Car Seat', 'Crib', 'Baby Clothes', 'Toys', 'Books'],
            'Electronics': ['Tablet', 'Laptop', 'Monitor', 'Keyboard', 'Mouse', 'Headphones'],
            'Sports': ['Basketball', 'Soccer Ball', 'Bike', 'Skateboard', 'Tennis Racket', 'Yoga Mat'],
            'Furniture': ['Desk', 'Chair', 'Table', 'Bookshelf', 'Lamp', 'Storage Bins'],
        }
        
        conditions = ['new', 'excellent', 'good', 'fair']
        condition_weights = [0.05, 0.25, 0.50, 0.20]
        
        items = []
        donors = [u for u in users if u.role in ['community_member', 'steward']]
        
        for category, item_names in categories_items.items():
            for item_name in item_names:
                # Create multiple instances across hubs
                for _ in range(random.randint(1, 3)):
                    hub = random.choice(hubs)
                    condition = random.choices(conditions, weights=condition_weights)[0]
                    qty_total = random.randint(1, 5)
                    qty_available = random.randint(0, qty_total)
                    
                    item = InventoryItem.objects.create(
                        hub=hub,
                        name=item_name,
                        description=self._generate_item_description(item_name, condition),
                        category=category,
                        tags=[category.lower(), item_name.lower().replace(' ', '-')],
                        condition=condition,
                        quantity_total=qty_total,
                        quantity_available=qty_available,
                        donor=random.choice(donors) if random.random() > 0.3 else None,
                        status='reserved' if qty_available == 0 else 'active'
                    )
                    items.append(item)
        
        self.stdout.write(f'  ✓ Created {len(items)} inventory items')
        return items

    def _generate_item_description(self, item_name, condition):
        """Generate realistic item descriptions"""
        templates = [
            f"Great condition {item_name.lower()} available for community use.",
            f"Well-maintained {item_name.lower()}, perfect for your needs.",
            f"{item_name} in {condition} condition. Has served our community well.",
            f"Donated {item_name.lower()}, works perfectly. Free to borrow.",
            f"Quality {item_name.lower()} ready to be shared with neighbors."
        ]
        return random.choice(templates)

    def _create_reservations(self, fake, users, items, hubs):
        """Create realistic reservations with proper states"""
        self.stdout.write('Creating reservations...')
        
        reservations = []
        borrowers = [u for u in users if u.role in ['newcomer', 'community_member']]
        
        # Create various reservation states
        states_config = [
            ('picked_up', 15, -7, 7),   # Currently borrowed
            ('pending', 8, 1, 14),       # Awaiting pickup
            ('confirmed', 5, 2, 10),     # Confirmed future
            ('overdue', 4, -14, -3),     # Overdue returns
            ('returned', 20, -30, -1),   # Past returns
        ]
        
        for status, count, days_from, days_to in states_config:
            for _ in range(count):
                user = random.choice(borrowers)
                # Pick item from user's hub or nearby
                available_items = [i for i in items if i.quantity_available > 0 and i.status == 'active']
                if not available_items:
                    continue
                    
                item = random.choice(available_items)
                
                pickup_date = date.today() + timedelta(days=random.randint(days_from, days_to))
                expected_return = pickup_date + timedelta(days=random.randint(7, 21))
                
                reservation = Reservation.objects.create(
                    user=user,
                    item=item,
                    hub=item.hub,
                    quantity=1,
                    status=status,
                    pickup_date=pickup_date,
                    expected_return_date=expected_return,
                    actual_return_date=expected_return + timedelta(days=random.randint(-2, 2)) if status == 'returned' else None
                )
                reservations.append(reservation)
                
                # Update item availability
                if status in ['picked_up', 'confirmed']:
                    item.quantity_available = max(0, item.quantity_available - 1)
                    if item.quantity_available == 0:
                        item.status = 'reserved'
                    item.save()
        
        self.stdout.write(f'  ✓ Created {len(reservations)} reservations')
        return reservations

    def _create_badges(self):
        """Create achievement badges"""
        self.stdout.write('Creating badges...')
        
        badges_data = [
            ('First Share', 'Shared your first item with the community', 'contribution', {'items_shared': 1}),
            ('Generous Giver', 'Shared 5+ items with neighbors', 'contribution', {'items_shared': 5}),
            ('Helpful Neighbor', 'Completed 10 successful borrows', 'community', {'successful_borrows': 10}),
            ('Community Champion', 'Active member for 6 months', 'milestone', {'membership_days': 180}),
            ('Mentorship Star', 'Actively mentoring a newcomer', 'mentorship', {'active_mentorships': 1}),
            ('Welcome Ambassador', 'Welcomed 5 new members', 'community', {'welcomes_sent': 5}),
            ('On-Time Returner', '100% on-time return rate', 'milestone', {'on_time_returns': 10}),
            ('Hub Supporter', 'Volunteered at 3+ hub events', 'contribution', {'events_attended': 3}),
        ]
        
        badges = []
        for name, desc, category, criteria in badges_data:
            badge = Badge.objects.create(
                name=name,
                description=desc,
                category=category,
                criteria=criteria
            )
            badges.append(badge)
        
        self.stdout.write(f'  ✓ Created {len(badges)} badges')
        return badges

    def _create_user_badges(self, users, badges):
        """Award badges to deserving users"""
        self.stdout.write('Awarding badges...')
        
        awarded = 0
        active_users = [u for u in users if u.role in ['community_member', 'steward']]
        
        for user in active_users:
            # Award 1-3 badges per active user
            num_badges = random.randint(1, 3)
            user_badges = random.sample(badges, min(num_badges, len(badges)))
            
            for badge in user_badges:
                days_ago = random.randint(1, 90)
                UserBadge.objects.create(
                    user=user,
                    badge=badge,
                    awarded_at=timezone.now() - timedelta(days=days_ago)
                )
                awarded += 1
        
        self.stdout.write(f'  ✓ Awarded {awarded} badges')

    def _create_mentorship_connections(self, fake, users):
        """Create mentorship connections"""
        self.stdout.write('Creating mentorship connections...')
        
        newcomers = [u for u in users if u.role == 'newcomer']
        mentors = [u for u in users if u.role in ['community_member', 'steward']]
        
        connections = []
        
        # Active mentorships
        for _ in range(min(8, len(newcomers))):
            if not mentors:
                break
            newcomer = random.choice(newcomers)
            mentor = random.choice(mentors)
            
            start = date.today() - timedelta(days=random.randint(5, 30))
            
            connection = MentorshipConnection.objects.create(
                mentor=mentor,
                mentee=newcomer,
                status='active',
                start_date=start
            )
            connections.append(connection)
            
            # Add some messages
            for _ in range(random.randint(2, 6)):
                days_ago = random.randint(0, 20)
                Message.objects.create(
                    connection=connection,
                    sender=random.choice([mentor, newcomer]),
                    content=fake.sentence(nb_words=random.randint(5, 15)),
                    created_at=timezone.now() - timedelta(days=days_ago)
                )
        
        # Requested mentorships
        for _ in range(3):
            if not mentors or not newcomers:
                break
            MentorshipConnection.objects.create(
                mentor=random.choice(mentors),
                mentee=random.choice(newcomers),
                status='requested'
            )
        
        self.stdout.write(f'  ✓ Created {len(connections)} active mentorships')

    def _create_events(self, fake, hubs, users):
        """Create hub events"""
        self.stdout.write('Creating events...')
        
        event_templates = [
            ('Community Dinner', 'community_dinner', 'Join us for a warm meal and conversation. All community members welcome.'),
            ('Newcomer Welcome Session', 'meeting', 'Meet other newcomers, learn about hub resources, and ask questions.'),
            ('Skill Share Workshop', 'workshop', 'Learn a new skill from community members. This week: basic home repairs.'),
            ('Volunteer Day', 'volunteer', 'Help organize the hub, sort donations, and prepare for the week ahead.'),
            ('Community Celebration', 'celebration', 'Celebrating our community achievements this quarter.'),
            ('Resource Fair', 'meeting', 'Connect with local services, partners, and community resources.'),
        ]
        
        events = []
        stewards = [u for u in users if u.role == 'steward']
        
        for hub in hubs:
            # Create 2-4 events per hub (past and future)
            for _ in range(random.randint(2, 4)):
                template = random.choice(event_templates)
                days_offset = random.randint(-30, 60)
                event_date = timezone.now() + timedelta(days=days_offset)
                
                event = Event.objects.create(
                    hub=hub,
                    title=template[0],
                    description=template[2],
                    event_type=template[1],
                    event_date=event_date,
                    duration_hours=Decimal(random.choice([1.5, 2.0, 2.5, 3.0])),
                    max_participants=random.randint(15, 40) if random.random() > 0.3 else None,
                    organizer=random.choice(stewards) if stewards else None
                )
                events.append(event)
        
        self.stdout.write(f'  ✓ Created {len(events)} events')

    def _create_announcements(self, fake, hubs, users):
        """Create hub announcements"""
        self.stdout.write('Creating announcements...')
        
        announcement_templates = [
            ('Extended Hours This Week', 'normal', 'The hub will be open late on Thursday and Friday to accommodate more visitors.'),
            ('New Winter Gear Donations', 'normal', 'We just received a large donation of winter coats, boots, and accessories. Come check them out!'),
            ('Hub Closed for Maintenance', 'high', 'The hub will be closed next Monday for maintenance. We apologize for any inconvenience.'),
            ('Volunteer Opportunities', 'normal', 'Looking for volunteers to help with weekend sorting. Sign up at the front desk.'),
            ('Safety Reminder', 'high', 'Please remember to sign in and out when visiting the hub. Your safety is our priority.'),
            ('New Partnership Announcement', 'normal', 'We\'ve partnered with Local Food Bank to better serve our community.'),
        ]
        
        announcements = []
        stewards = [u for u in users if u.role == 'steward']
        
        for hub in hubs:
            # 2-3 announcements per hub
            for _ in range(random.randint(2, 3)):
                template = random.choice(announcement_templates)
                days_ago = random.randint(1, 14)
                active_days = random.randint(7, 30)
                
                announcement = Announcement.objects.create(
                    hub=hub,
                    title=template[0],
                    content=template[2],
                    priority=template[1],
                    author=random.choice(stewards) if stewards else None,
                    active_until=date.today() + timedelta(days=active_days),
                    created_at=timezone.now() - timedelta(days=days_ago)
                )
                announcements.append(announcement)
        
        self.stdout.write(f'  ✓ Created {len(announcements)} announcements')

    def _create_feedback(self, fake, users, items, reservations):
        """Create user feedback entries"""
        self.stdout.write('Creating feedback...')
        
        feedback_list = []
        
        # Positive feedback (70%)
        positive_templates = [
            "The item was exactly what I needed. Thank you!",
            "Great condition and very helpful staff.",
            "This really helped my family. Grateful for the community support.",
            "Easy process and the item worked perfectly.",
            "Clean and well-maintained. Will borrow again."
        ]
        
        # Constructive feedback (25%)
        negative_templates = [
            "Item was not as described, could use better photos.",
            "Pickup time wasn't convenient, wish there were more options.",
            "Item condition was worse than expected.",
            "Process was confusing as a first-time user."
        ]
        
        # Incident reports (5%)
        incident_templates = [
            "Item was damaged during my use. Reported to steward.",
            "Lost a small part of the item. Will replace before returning.",
            "Item stopped working during use."
        ]
        
        feedback_configs = [
            ('positive', 20, positive_templates, 4, 5),
            ('negative', 7, negative_templates, 2, 3),
            ('incident', 3, incident_templates, None, None),
        ]
        
        for feedback_type, count, templates, rating_min, rating_max in feedback_configs:
            for _ in range(count):
                user = random.choice(users)
                reservation = random.choice(reservations) if reservations else None
                
                feedback = Feedback.objects.create(
                    user=user,
                    item=reservation.item if reservation else random.choice(items),
                    reservation=reservation,
                    type=feedback_type,
                    rating=random.randint(rating_min, rating_max) if rating_min else None,
                    comment=random.choice(templates),
                    status=random.choice(['pending', 'reviewed', 'resolved']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60))
                )
                feedback_list.append(feedback)
        
        self.stdout.write(f'  ✓ Created {len(feedback_list)} feedback entries')
