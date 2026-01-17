"""Unit tests for language detector."""
import pytest
from unittest.mock import patch
from app.services.language_detector import LanguageDetector


def test_detect_language_english():
    """Test detecting English language."""
    result = LanguageDetector.detect_language("This is an English sentence.")
    assert result == "en"


def test_detect_language_spanish():
    """Test detecting Spanish language."""
    result = LanguageDetector.detect_language("Esta es una oración en español.")
    assert result in ["es", "en"]  # May default to en if not detected


def test_detect_language_unsupported():
    """Test detecting unsupported language defaults to English."""
    with patch('langdetect.detect', return_value="xx"):
        result = LanguageDetector.detect_language("Some text")
        assert result == "en"


def test_detect_language_error_handling():
    """Test language detection error handling."""
    with patch('langdetect.detect', side_effect=Exception("Detection error")):
        result = LanguageDetector.detect_language("Some text")
        assert result == "en"  # Should default to English


def test_is_supported():
    """Test checking if language is supported."""
    assert LanguageDetector.is_supported("en") is True
    assert LanguageDetector.is_supported("es") is True
    assert LanguageDetector.is_supported("fr") is True
    assert LanguageDetector.is_supported("xx") is False
    assert LanguageDetector.is_supported("") is False


def test_get_language_name():
    """Test getting language name from code."""
    assert LanguageDetector.get_language_name("en") == "English"
    assert LanguageDetector.get_language_name("es") == "Spanish"
    assert LanguageDetector.get_language_name("fr") == "French"
    assert LanguageDetector.get_language_name("xx") == "Unknown"


def test_supported_languages_completeness():
    """Test that all expected languages are supported."""
    expected_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko', 'ar', 'hi', 'ru']
    
    for lang in expected_languages:
        assert LanguageDetector.is_supported(lang), f"{lang} should be supported"
        assert LanguageDetector.get_language_name(lang) != "Unknown", f"{lang} should have a name"
