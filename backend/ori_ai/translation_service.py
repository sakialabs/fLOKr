"""
Ori AI - Translation Service
Provides multilingual translation with caching and language detection
"""
import logging
from typing import Dict, Optional, List
from django.core.cache import cache
from django.conf import settings
import hashlib

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Manages translation of content with caching for performance
    Supports multiple translation backends
    """
    
    SUPPORTED_LANGUAGES = [
        'en', 'es', 'ar', 'fr', 'zh', 'ur', 'so', 'am', 'ru', 'fa', 'sw'
    ]
    
    LANGUAGE_NAMES = {
        'en': 'English',
        'es': 'Spanish',
        'ar': 'Arabic',
        'fr': 'French',
        'zh': 'Chinese',
        'ur': 'Urdu',
        'so': 'Somali',
        'am': 'Amharic',
        'ru': 'Russian',
        'fa': 'Farsi',
        'sw': 'Swahili'
    }
    
    def __init__(self):
        self.cache_ttl = getattr(settings, 'TRANSLATION_CACHE_TTL', 86400)  # 24 hours
        self.backend = self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize translation backend based on settings"""
        backend_type = getattr(settings, 'TRANSLATION_BACKEND', 'google')
        
        if backend_type == 'google':
            return GoogleTranslateBackend()
        elif backend_type == 'libretranslate':
            return LibreTranslateBackend()
        else:
            return MockTranslateBackend()  # For development/testing
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        content = f"{text}:{source_lang}:{target_lang}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        return f"translation:{hash_key}"
    
    def translate(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            Dict with 'translated_text', 'source_lang', 'target_lang', 'cached'
        """
        # Validate target language
        if target_lang not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported target language: {target_lang}")
            return {
                'translated_text': text,
                'source_lang': source_lang or 'unknown',
                'target_lang': target_lang,
                'cached': False,
                'error': 'Unsupported target language'
            }
        
        # If no source language, detect it
        if not source_lang:
            source_lang = self.detect_language(text)
        
        # If source and target are the same, return original
        if source_lang == target_lang:
            return {
                'translated_text': text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'cached': False
            }
        
        # Check cache
        cache_key = self._get_cache_key(text, source_lang, target_lang)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            cached_result['cached'] = True
            return cached_result
        
        # Translate using backend
        try:
            translated_text = self.backend.translate(text, source_lang, target_lang)
            
            result = {
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'cached': False
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                'translated_text': text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'cached': False,
                'error': str(e)
            }
    
    def translate_batch(
        self,
        texts: List[str],
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Translate multiple texts at once
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            List of translation results
        """
        return [
            self.translate(text, target_lang, source_lang)
            for text in texts
        ]
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code
        """
        try:
            return self.backend.detect_language(text)
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'  # Default to English
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with names"""
        return [
            {'code': code, 'name': name}
            for code, name in self.LANGUAGE_NAMES.items()
        ]


class GoogleTranslateBackend:
    """Google Translate API backend"""
    
    def __init__(self):
        try:
            from google.cloud import translate_v2 as translate
            self.client = translate.Client()
        except Exception as e:
            logger.warning(f"Google Translate not available: {str(e)}")
            self.client = None
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using Google Translate"""
        if not self.client:
            raise Exception("Google Translate client not initialized")
        
        result = self.client.translate(
            text,
            source_language=source_lang,
            target_language=target_lang
        )
        return result['translatedText']
    
    def detect_language(self, text: str) -> str:
        """Detect language using Google Translate"""
        if not self.client:
            return 'en'
        
        result = self.client.detect_language(text)
        return result['language']


class LibreTranslateBackend:
    """LibreTranslate API backend (open source alternative)"""
    
    def __init__(self):
        import requests
        self.api_url = getattr(settings, 'LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
        self.api_key = getattr(settings, 'LIBRETRANSLATE_API_KEY', None)
        self.session = requests.Session()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using LibreTranslate"""
        payload = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        if self.api_key:
            payload['api_key'] = self.api_key
        
        response = self.session.post(self.api_url, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json()['translatedText']
    
    def detect_language(self, text: str) -> str:
        """Detect language using LibreTranslate"""
        detect_url = self.api_url.replace('/translate', '/detect')
        payload = {'q': text}
        
        if self.api_key:
            payload['api_key'] = self.api_key
        
        response = self.session.post(detect_url, json=payload, timeout=10)
        response.raise_for_status()
        
        detections = response.json()
        if detections and len(detections) > 0:
            return detections[0]['language']
        return 'en'


class MockTranslateBackend:
    """Mock backend for development/testing"""
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Return text with language prefix for testing"""
        return f"[{target_lang.upper()}] {text}"
    
    def detect_language(self, text: str) -> str:
        """Always return English for testing"""
        return 'en'


# Singleton instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get or create translation service singleton"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
