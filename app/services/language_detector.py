"""Language detection and translation utilities."""
from langdetect import detect, DetectorFactory
from typing import Optional
import logging

# Set seed for consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects and validates language from text."""
    
    # Supported languages mapping
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ru': 'Russian',
    }
    
    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            detected = detect(text)
            # Validate detected language is supported
            if detected in cls.SUPPORTED_LANGUAGES:
                logger.info(f"Detected language: {detected} ({cls.SUPPORTED_LANGUAGES[detected]})")
                return detected
            else:
                logger.warning(f"Unsupported language detected: {detected}, defaulting to English")
                return 'en'
        except Exception as e:
            logger.error(f"Language detection failed: {e}, defaulting to English")
            return 'en'
    
    @classmethod
    def is_supported(cls, language_code: str) -> bool:
        """Check if a language code is supported."""
        return language_code in cls.SUPPORTED_LANGUAGES
    
    @classmethod
    def get_language_name(cls, language_code: str) -> str:
        """Get the full name of a language from its code."""
        return cls.SUPPORTED_LANGUAGES.get(language_code, 'Unknown')
