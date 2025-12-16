"""
Tests for Ori AI services
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from .image_tagger import ImageTagger, get_image_tagger


class ImageTaggerTests(TestCase):
    """Tests for image tagging service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tagger = get_image_tagger()
    
    def create_test_image(self, size=(224, 224), color='RGB'):
        """Create a test image"""
        image = Image.new(color, size, color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        return buffer.getvalue()
    
    def test_image_tagger_initialization(self):
        """Test that image tagger initializes correctly"""
        self.assertIsNotNone(self.tagger.model)
        self.assertIsNotNone(self.tagger.transform)
        self.assertIsNotNone(self.tagger.labels)
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        image_data = self.create_test_image()
        tensor = self.tagger.preprocess_image(image_data)
        
        # Check tensor shape (batch_size, channels, height, width)
        self.assertEqual(tensor.shape, (1, 3, 224, 224))
    
    def test_generate_tags(self):
        """Test tag generation"""
        image_data = self.create_test_image()
        tags = self.tagger.generate_tags(image_data, top_k=5)
        
        # Should return 5 tags
        self.assertEqual(len(tags), 5)
        
        # Each tag should have 'tag' and 'confidence' keys
        for tag in tags:
            self.assertIn('tag', tag)
            self.assertIn('confidence', tag)
            self.assertIsInstance(tag['tag'], str)
            self.assertIsInstance(tag['confidence'], float)
            self.assertGreaterEqual(tag['confidence'], 0.0)
            self.assertLessEqual(tag['confidence'], 1.0)
    
    def test_classify_category(self):
        """Test category classification"""
        tags = [
            {'tag': 'clothing', 'confidence': 0.8},
            {'tag': 'shirt', 'confidence': 0.6}
        ]
        category = self.tagger.classify_category(tags)
        self.assertEqual(category, 'clothing')
    
    def test_suggest_tags_and_category(self):
        """Test combined tag and category suggestion"""
        image_data = self.create_test_image()
        tags, category = self.tagger.suggest_tags_and_category(image_data)
        
        # Should return tags and category
        self.assertIsInstance(tags, list)
        self.assertIsInstance(category, str)
        self.assertGreater(len(tags), 0)
    
    def test_invalid_image_data(self):
        """Test handling of invalid image data"""
        with self.assertRaises(ValueError):
            self.tagger.preprocess_image(b'invalid image data')
    
    def test_singleton_instance(self):
        """Test that get_image_tagger returns singleton"""
        tagger1 = get_image_tagger()
        tagger2 = get_image_tagger()
        self.assertIs(tagger1, tagger2)
