"""
Tests for Ori AI image tagging integration with inventory
"""
import io
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from hubs.models import Hub
from .models import InventoryItem

User = get_user_model()


class ImageTaggingIntegrationTests(TestCase):
    """Tests for automatic image tagging in inventory"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        # Create test user (steward)
        self.user = User.objects.create_user(
            email='steward@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Steward',
            role='steward'
        )
        
        # Create test hub
        self.hub = Hub.objects.create(
            name='Test Hub',
            address='123 Test St',
            location='POINT(-122.4194 37.7749)'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (224, 224), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer
    
    def test_suggest_tags_endpoint(self):
        """Test the suggest_tags endpoint"""
        image_file = self.create_test_image()
        
        response = self.client.post(
            '/api/inventory/items/suggest_tags/',
            {'image': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
        self.assertIn('category', response.data)
        self.assertIn('detailed_tags', response.data)
        self.assertIsInstance(response.data['tags'], list)
        self.assertIsInstance(response.data['category'], str)
    
    def test_auto_tagging_on_item_creation(self):
        """Test automatic tagging when creating an item"""
        # Note: This test requires mocking the image URL download
        # In a real scenario, you'd upload to S3 first
        
        data = {
            'name': 'Test Item',
            'description': 'Test description',
            'hub': self.hub.id,
            'quantity_total': 1,
            'quantity_available': 1,
            'auto_tag': True,
            'images': []  # Would contain actual image URLs
        }
        
        response = self.client.post(
            '/api/inventory/items/',
            data,
            format='json'
        )
        
        # Should succeed even without images
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
    
    def test_auto_tagging_disabled(self):
        """Test that auto-tagging can be disabled"""
        data = {
            'name': 'Test Item',
            'description': 'Test description',
            'hub': self.hub.id,
            'quantity_total': 1,
            'quantity_available': 1,
            'auto_tag': False,  # Disable auto-tagging
            'tags': ['manual', 'tags'],
            'category': 'other'
        }
        
        response = self.client.post(
            '/api/inventory/items/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should use manual tags, not AI suggestions
        item = InventoryItem.objects.get(id=response.data['id'])
        self.assertEqual(item.category, 'other')
        self.assertIn('manual', item.tags)
    
    def test_suggest_tags_requires_authentication(self):
        """Test that suggest_tags requires authentication"""
        self.client.force_authenticate(user=None)
        
        image_file = self.create_test_image()
        response = self.client.post(
            '/api/inventory/items/suggest_tags/',
            {'image': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_suggest_tags_requires_steward_role(self):
        """Test that suggest_tags requires steward or admin role"""
        # Create regular user
        regular_user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Regular',
            last_name='User',
            role='newcomer'
        )
        
        self.client.force_authenticate(user=regular_user)
        
        image_file = self.create_test_image()
        response = self.client.post(
            '/api/inventory/items/suggest_tags/',
            {'image': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
