"""
Management command to seed FAQ database with common questions
"""
from django.core.management.base import BaseCommand
from ori_ai.models import FAQEntry


class Command(BaseCommand):
    help = 'Seed FAQ database with common questions and answers'
    
    def handle(self, *args, **options):
        """Seed FAQ entries"""
        
        faqs = [
            # General
            {
                'question': 'What is fLOKr?',
                'answer': 'fLOKr is a community resource sharing platform that connects newcomers with essential items and mentorship. We help you borrow household items, connect with mentors, and integrate into your new community.',
                'category': 'general',
                'keywords': ['flokr', 'platform', 'about', 'what is']
            },
            {
                'question': 'How does fLOKr work?',
                'answer': 'fLOKr works through community hubs where you can browse available items, make reservations, and pick them up. You can also connect with mentors and participate in community activities.',
                'category': 'general',
                'keywords': ['how', 'works', 'process']
            },
            
            # Borrowing
            {
                'question': 'How do I borrow an item?',
                'answer': 'To borrow an item: 1) Search for the item you need, 2) Click "Reserve" and select pickup/return dates, 3) Visit your assigned hub during operating hours to pick it up, 4) Return it by the due date.',
                'category': 'borrowing',
                'keywords': ['borrow', 'reserve', 'how to', 'process']
            },
            {
                'question': 'How long can I borrow items?',
                'answer': 'Most items can be borrowed for 7-14 days. The specific duration depends on the item type and demand. You can request an extension if you need more time.',
                'category': 'borrowing',
                'keywords': ['duration', 'how long', 'time', 'period']
            },
            {
                'question': 'Can I extend my borrowing period?',
                'answer': 'Yes! You can request an extension through the app before your due date. Your hub steward will review and approve extensions based on item availability.',
                'category': 'borrowing',
                'keywords': ['extend', 'extension', 'more time', 'longer']
            },
            {
                'question': 'What happens if I return an item late?',
                'answer': 'We understand things happen! However, repeated late returns (3 or more) may temporarily restrict your borrowing privileges to ensure fairness for all community members.',
                'category': 'borrowing',
                'keywords': ['late', 'overdue', 'penalty', 'restriction']
            },
            
            # Inventory
            {
                'question': 'What items are available to borrow?',
                'answer': 'We have a wide range of items including furniture (beds, tables, chairs), kitchen supplies (pots, dishes, utensils), cleaning equipment, winter clothing, baby items, and more. Browse the inventory to see what\'s available at your hub.',
                'category': 'inventory',
                'keywords': ['items', 'available', 'what', 'inventory']
            },
            {
                'question': 'How do I search for specific items?',
                'answer': 'Use the search bar on the home screen or browse by category. You can filter by condition, location, and availability. Items at your assigned hub appear first.',
                'category': 'inventory',
                'keywords': ['search', 'find', 'look for']
            },
            
            # Hubs
            {
                'question': 'What is a hub?',
                'answer': 'A hub is a physical community center where items are stored and distributed. Each hub is managed by stewards who help coordinate borrowing and returns.',
                'category': 'hubs',
                'keywords': ['hub', 'what is', 'location', 'center']
            },
            {
                'question': 'How do I find my nearest hub?',
                'answer': 'Your nearest hub is automatically assigned based on your address. You can view hub locations, operating hours, and directions in the Hubs section of the app.',
                'category': 'hubs',
                'keywords': ['find', 'nearest', 'location', 'where']
            },
            {
                'question': 'What are hub operating hours?',
                'answer': 'Operating hours vary by hub. Most hubs are open weekdays 9 AM - 5 PM and some weekends. Check your specific hub\'s hours in the app.',
                'category': 'hubs',
                'keywords': ['hours', 'open', 'when', 'schedule']
            },
            
            # Mentorship
            {
                'question': 'How do I find a mentor?',
                'answer': 'Go to the Mentorship section and browse available mentors. You can filter by language, interests, and location. Send a connection request to mentors you\'d like to connect with.',
                'category': 'mentorship',
                'keywords': ['mentor', 'find', 'connect', 'match']
            },
            {
                'question': 'What does a mentor do?',
                'answer': 'Mentors provide guidance, answer questions about settling in, share local knowledge, and offer friendship. They can help with everything from navigating services to cultural adjustment.',
                'category': 'mentorship',
                'keywords': ['mentor', 'role', 'what', 'help']
            },
            {
                'question': 'Can I become a mentor?',
                'answer': 'Yes! If you\'ve been in the community for a while and want to help newcomers, you can enable the mentor flag in your profile settings.',
                'category': 'mentorship',
                'keywords': ['become', 'mentor', 'volunteer', 'help']
            },
            
            # Community
            {
                'question': 'What are badges?',
                'answer': 'Badges are awards you earn for contributing to the community - like donating items, helping others, or completing mentorships. They appear on your profile and celebrate your contributions.',
                'category': 'community',
                'keywords': ['badges', 'awards', 'achievements']
            },
            {
                'question': 'How do I earn reputation points?',
                'answer': 'You earn reputation points through positive feedback from other community members, returning items on time, donating items, and being a helpful mentor.',
                'category': 'community',
                'keywords': ['reputation', 'points', 'score', 'earn']
            },
            
            # Account
            {
                'question': 'How do I create an account?',
                'answer': 'Download the fLOKr app, click "Sign Up", enter your email and create a password. You\'ll complete a short onboarding to set your preferences and get assigned to a hub.',
                'category': 'account',
                'keywords': ['create', 'account', 'sign up', 'register']
            },
            {
                'question': 'How do I reset my password?',
                'answer': 'On the login screen, click "Forgot Password". Enter your email and we\'ll send you a reset link. Follow the link to create a new password.',
                'category': 'account',
                'keywords': ['password', 'reset', 'forgot', 'change']
            },
            {
                'question': 'How do I change my language preference?',
                'answer': 'Go to Settings > Language and select your preferred language. The app interface and recommendations will be translated to your chosen language.',
                'category': 'account',
                'keywords': ['language', 'change', 'translate', 'preference']
            },
            
            # Technical
            {
                'question': 'The app is not working. What should I do?',
                'answer': 'Try these steps: 1) Close and restart the app, 2) Check your internet connection, 3) Update to the latest version, 4) Clear app cache in settings. If problems persist, contact support.',
                'category': 'technical',
                'keywords': ['not working', 'broken', 'error', 'problem']
            },
            {
                'question': 'How do I report a problem with an item?',
                'answer': 'Use the "Report Issue" button on the item page or in your reservation. Describe the problem and it will be sent to the hub steward for review.',
                'category': 'technical',
                'keywords': ['report', 'problem', 'issue', 'broken']
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for faq_data in faqs:
            faq, created = FAQEntry.objects.update_or_create(
                question=faq_data['question'],
                defaults={
                    'answer': faq_data['answer'],
                    'category': faq_data['category'],
                    'keywords': faq_data['keywords'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {created_count} new FAQs '
                f'and updated {updated_count} existing FAQs'
            )
        )
