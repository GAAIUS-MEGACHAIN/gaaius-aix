"""
Auto-Translator Service
Provides translation capabilities for 50+ languages across the platform.
Supports language detection, caching, and multi-platform integration.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from uuid import uuid4
import hashlib
from functools import lru_cache

# Translation library with fallback
try:
    from googletrans import Translator as GoogleTranslator, LANGUAGES
    TRANSLATOR_AVAILABLE = True
    TRANSLATOR_TYPE = "google"
except ImportError:
    TRANSLATOR_AVAILABLE = False
    TRANSLATOR_TYPE = None
    LANGUAGES = {}

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages (50+)"""
    # European Languages
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    POLISH = "pl"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    GREEK = "el"
    HUNGARIAN = "hu"
    CZECH = "cs"
    SLOVAK = "sk"
    ROMANIAN = "ro"
    BULGARIAN = "bg"
    CROATIAN = "hr"
    
    # Asian Languages
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    JAPANESE = "ja"
    KOREAN = "ko"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    TAGALOG = "tl"
    BENGALI = "bn"
    HINDI = "hi"
    MARATHI = "mr"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    URDU = "ur"
    PUNJABI = "pa"
    GUJARATI = "gu"
    
    # Middle Eastern & African Languages
    ARABIC = "ar"
    HEBREW = "he"
    PERSIAN = "fa"
    TURKISH = "tr"
    AFRIKAANS = "af"
    SWAHILI = "sw"
    IGBO = "ig"
    YORUBA = "yo"
    SOMALI = "so"
    AMHARIC = "am"
    
    # American Languages
    PORTUGUESE_BRAZILIAN = "pt-BR"
    MEXICAN_SPANISH = "es-MX"


LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "pl": "Polish",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "el": "Greek",
    "hu": "Hungarian",
    "cs": "Czech",
    "sk": "Slovak",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "tl": "Tagalog",
    "bn": "Bengali",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ur": "Urdu",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "ar": "Arabic",
    "he": "Hebrew",
    "fa": "Persian",
    "tr": "Turkish",
    "af": "Afrikaans",
    "sw": "Swahili",
    "ig": "Igbo",
    "yo": "Yoruba",
    "so": "Somali",
    "am": "Amharic",
    "pt-BR": "Portuguese (Brazilian)",
    "es-MX": "Spanish (Mexican)",
}


@dataclass
class TranslationResult:
    """Result of a translation operation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    original_text: str = ""
    translated_text: str = ""
    source_language: str = "en"
    target_language: str = "en"
    detected_language: Optional[str] = None
    confidence: float = 1.0
    is_cached: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class LanguagePreference:
    """User language preference"""
    user_id: str
    primary_language: str = "en"
    secondary_languages: List[str] = field(default_factory=list)
    auto_translate: bool = True
    translation_history_limit: int = 100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class AutoTranslator:
    """Main auto-translator service"""
    
    def __init__(self):
        """Initialize translator"""
        self.translator = GoogleTranslator() if TRANSLATOR_AVAILABLE else None
        self.translation_cache: Dict[str, TranslationResult] = {}
        self.user_preferences: Dict[str, LanguagePreference] = {}
        self.cache_expiry = timedelta(hours=24)
        self.max_cache_size = 10000
        logger.info(f"AutoTranslator initialized with backend: {TRANSLATOR_TYPE}")
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key using SHA256 for security"""
        key_str = f"{text}|{source_lang}|{target_lang}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def detect_language(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect the language of given text
        
        Args:
            text: Text to detect language from
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text or len(text.strip()) < 2:
            return None, 0.0
        
        if not self.translator:
            return None, 0.0
        
        try:
            detection = self.translator.detect(text)
            if isinstance(detection, dict):
                return detection.get('lang', 'en'), detection.get('confidence', 0.5)
            else:
                # Handle if detection returns object with lang attribute
                return getattr(detection, 'lang', 'en'), getattr(detection, 'confidence', 0.5)
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return None, 0.0
    
    def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        use_cache: bool = True
    ) -> TranslationResult:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            source_language: Source language code (or "auto" for detection)
            target_language: Target language code
            use_cache: Whether to use cache
            
        Returns:
            TranslationResult object
        """
        if not text or len(text.strip()) == 0:
            return TranslationResult(
                original_text="",
                translated_text="",
                source_language=source_language,
                target_language=target_language
            )
        
        # Same language - no translation needed
        if source_language == target_language and source_language != "auto":
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence=1.0
            )
        
        # Auto-detect source language
        if source_language.lower() == "auto":
            detected, confidence = self.detect_language(text)
            source_language = detected or "en"
        else:
            confidence = 1.0
        
        # Check cache
        cache_key = self._get_cache_key(text, source_language, target_language)
        if use_cache and cache_key in self.translation_cache:
            cached = self.translation_cache[cache_key]
            cached.is_cached = True
            logger.debug(f"Cache hit for {source_language} -> {target_language}")
            return cached
        
        # Translate
        if not self.translator:
            logger.warning("Translator not available, returning original text")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence=0.0
            )
        
        try:
            translation = self.translator.translate(
                text,
                src_lang=source_language,
                dest_lang=target_language
            )
            
            # Handle both dict and object responses
            if isinstance(translation, dict):
                translated_text = translation.get('text', text)
            else:
                translated_text = getattr(translation, 'text', text)
            
            result = TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                detected_language=source_language,
                confidence=confidence,
                is_cached=False
            )
            
            # Cache result
            if use_cache:
                if len(self.translation_cache) >= self.max_cache_size:
                    # Simple FIFO eviction
                    oldest_key = next(iter(self.translation_cache))
                    del self.translation_cache[oldest_key]
                
                self.translation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence=0.0
            )
    
    def translate_batch(
        self,
        texts: List[str],
        source_language: str = "auto",
        target_language: str = "en"
    ) -> List[TranslationResult]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_language: Source language code
            target_language: Target language code
            
        Returns:
            List of TranslationResult objects
        """
        results = []
        for text in texts:
            result = self.translate(text, source_language, target_language)
            results.append(result)
        return results
    
    def set_user_preference(
        self,
        user_id: str,
        primary_language: str = "en",
        secondary_languages: Optional[List[str]] = None,
        auto_translate: bool = True
    ) -> LanguagePreference:
        """
        Set user language preference
        
        Args:
            user_id: User ID
            primary_language: Primary language code
            secondary_languages: List of secondary language codes
            auto_translate: Enable auto-translation
            
        Returns:
            LanguagePreference object
        """
        pref = LanguagePreference(
            user_id=user_id,
            primary_language=primary_language,
            secondary_languages=secondary_languages or [],
            auto_translate=auto_translate
        )
        self.user_preferences[user_id] = pref
        logger.info(f"Language preference set for user {user_id}: {primary_language}")
        return pref
    
    def get_user_preference(self, user_id: str) -> Optional[LanguagePreference]:
        """
        Get user language preference
        
        Args:
            user_id: User ID
            
        Returns:
            LanguagePreference or None
        """
        return self.user_preferences.get(user_id)
    
    def auto_translate_message(
        self,
        text: str,
        recipient_user_id: str,
        sender_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Auto-translate message for recipient based on their preference
        
        Args:
            text: Message text
            recipient_user_id: Recipient user ID
            sender_language: Sender's language (auto-detect if not provided)
            
        Returns:
            Dict with original and translated content
        """
        recipient_pref = self.get_user_preference(recipient_user_id)
        
        if not recipient_pref or not recipient_pref.auto_translate:
            return {
                "original": text,
                "translated": text,
                "source_language": sender_language or "unknown",
                "target_language": "en",
                "auto_translated": False
            }
        
        # Detect sender language if not provided
        if not sender_language:
            sender_language, _ = self.detect_language(text)
            sender_language = sender_language or "en"
        
        # Skip if same language
        if sender_language == recipient_pref.primary_language:
            return {
                "original": text,
                "translated": text,
                "source_language": sender_language,
                "target_language": recipient_pref.primary_language,
                "auto_translated": False
            }
        
        # Translate
        result = self.translate(
            text,
            source_language=sender_language,
            target_language=recipient_pref.primary_language
        )
        
        return {
            "original": result.original_text,
            "translated": result.translated_text,
            "source_language": result.source_language,
            "target_language": recipient_pref.primary_language,
            "auto_translated": True,
            "confidence": result.confidence
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of all supported languages
        
        Returns:
            Dict mapping language codes to language names
        """
        return LANGUAGE_NAMES.copy()
    
    def clear_cache(self) -> None:
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.translation_cache),
            "max_cache_size": self.max_cache_size,
            "cache_usage_percent": (len(self.translation_cache) / self.max_cache_size) * 100,
            "preferences_count": len(self.user_preferences)
        }
    
    def translate_content_for_platform(
        self,
        content: Dict[str, Any],
        source_language: str = "en",
        target_language: str = "en",
        fields_to_translate: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Translate specific fields in content object (for music, movies, videos, etc.)
        
        Args:
            content: Content object
            source_language: Source language
            target_language: Target language
            fields_to_translate: List of field names to translate
            
        Returns:
            Content with translated fields
        """
        if not fields_to_translate:
            fields_to_translate = ["title", "description", "tags", "caption"]
        
        translated_content = content.copy()
        
        for field in fields_to_translate:
            if field in content and isinstance(content[field], str):
                result = self.translate(
                    content[field],
                    source_language,
                    target_language
                )
                translated_content[f"{field}_translated"] = result.translated_text
                translated_content[f"{field}_language"] = target_language
        
        return translated_content
    
    def get_language_stats(self) -> Dict[str, int]:
        """Get statistics about translation requests"""
        stats = {}
        for cache_result in self.translation_cache.values():
            key = f"{cache_result.source_language}→{cache_result.target_language}"
            stats[key] = stats.get(key, 0) + 1
        return stats


# Global instance
auto_translator = AutoTranslator()


def get_translator() -> AutoTranslator:
    """Get translator instance"""
    return auto_translator
