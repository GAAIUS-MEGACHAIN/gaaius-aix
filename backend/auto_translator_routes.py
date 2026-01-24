"""
Auto-Translator API Routes
REST endpoints for translation, language detection, and user preferences.
"""

from fastapi import APIRouter, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from auto_translator import (
    get_translator,
    Language,
    TranslationResult,
    LanguagePreference,
    LANGUAGE_NAMES
)

logger = logging.getLogger(__name__)

# Create routers
router_translate = APIRouter(prefix="/api/translate", tags=["Translate"])
router_languages = APIRouter(prefix="/api/languages", tags=["Languages"])
router_preferences = APIRouter(prefix="/api/language-preferences", tags=["Language Preferences"])

# ============================================================================
# Request/Response Models
# ============================================================================

class TranslateRequest(BaseModel):
    """Request to translate text"""
    text: str = Field(..., min_length=1, description="Text to translate")
    source_language: str = Field(default="auto", description="Source language code (auto for detection)")
    target_language: str = Field(default="en", description="Target language code")
    use_cache: bool = Field(default=True, description="Use translation cache")


class TranslateBatchRequest(BaseModel):
    """Request to translate multiple texts"""
    texts: List[str] = Field(..., min_length=1, description="Texts to translate")
    source_language: str = Field(default="auto", description="Source language code")
    target_language: str = Field(default="en", description="Target language code")


class TranslateResponse(BaseModel):
    """Response from translation"""
    id: str
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    detected_language: Optional[str] = None
    confidence: float
    is_cached: bool
    timestamp: str


class DetectLanguageRequest(BaseModel):
    """Request to detect language"""
    text: str = Field(..., min_length=1, description="Text to detect language from")


class DetectLanguageResponse(BaseModel):
    """Response from language detection"""
    detected_language: Optional[str]
    language_name: Optional[str]
    confidence: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LanguagePreferenceRequest(BaseModel):
    """Request to set language preference"""
    user_id: str = Field(..., description="User ID")
    primary_language: str = Field(default="en", description="Primary language code")
    secondary_languages: List[str] = Field(default=[], description="Secondary language codes")
    auto_translate: bool = Field(default=True, description="Enable auto-translation")


class LanguagePreferenceResponse(BaseModel):
    """Response with language preference"""
    user_id: str
    primary_language: str
    secondary_languages: List[str]
    auto_translate: bool
    created_at: str
    updated_at: str


class AutoTranslateMessageRequest(BaseModel):
    """Request to auto-translate message for recipient"""
    text: str = Field(..., description="Message text")
    recipient_user_id: str = Field(..., description="Recipient user ID")
    sender_language: Optional[str] = Field(None, description="Sender's language")


class AutoTranslateMessageResponse(BaseModel):
    """Response from auto-translate message"""
    original: str
    translated: str
    source_language: str
    target_language: str
    auto_translated: bool
    confidence: Optional[float] = None


# ============================================================================
# Translation Endpoints
# ============================================================================

@router_translate.post("/", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text to target language
    
    - **text**: Text to translate
    - **source_language**: Source language code (use "auto" for auto-detection)
    - **target_language**: Target language code (default: "en")
    - **use_cache**: Use cached translations if available
    """
    try:
        translator = get_translator()
        result = translator.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            use_cache=request.use_cache
        )
        
        return TranslateResponse(
            id=result.id,
            original_text=result.original_text,
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
            detected_language=result.detected_language,
            confidence=result.confidence,
            is_cached=result.is_cached,
            timestamp=result.timestamp
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_translate.post("/batch", response_model=List[TranslateResponse])
async def translate_batch(request: TranslateBatchRequest):
    """
    Translate multiple texts
    
    - **texts**: List of texts to translate
    - **source_language**: Source language code
    - **target_language**: Target language code
    """
    try:
        translator = get_translator()
        results = translator.translate_batch(
            texts=request.texts,
            source_language=request.source_language,
            target_language=request.target_language
        )
        
        return [
            TranslateResponse(
                id=result.id,
                original_text=result.original_text,
                translated_text=result.translated_text,
                source_language=result.source_language,
                target_language=result.target_language,
                detected_language=result.detected_language,
                confidence=result.confidence,
                is_cached=result.is_cached,
                timestamp=result.timestamp
            )
            for result in results
        ]
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_translate.post("/detect", response_model=DetectLanguageResponse)
async def detect_language(request: DetectLanguageRequest):
    """
    Detect the language of given text
    
    - **text**: Text to detect language from
    """
    try:
        translator = get_translator()
        detected_lang, confidence = translator.detect_language(request.text)
        
        language_name = None
        if detected_lang:
            language_name = LANGUAGE_NAMES.get(detected_lang, detected_lang)
        
        return DetectLanguageResponse(
            detected_language=detected_lang,
            language_name=language_name,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_translate.post("/auto-translate-message", response_model=AutoTranslateMessageResponse)
async def auto_translate_message(request: AutoTranslateMessageRequest):
    """
    Auto-translate message for recipient based on their language preference
    
    - **text**: Message text
    - **recipient_user_id**: Recipient's user ID
    - **sender_language**: Sender's language (optional, auto-detected if not provided)
    """
    try:
        translator = get_translator()
        result = translator.auto_translate_message(
            text=request.text,
            recipient_user_id=request.recipient_user_id,
            sender_language=request.sender_language
        )
        
        return AutoTranslateMessageResponse(**result)
    except Exception as e:
        logger.error(f"Auto-translate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Language Management Endpoints
# ============================================================================

@router_languages.get("/supported")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of all supported languages"""
    try:
        translator = get_translator()
        languages = translator.get_supported_languages()
        
        return {
            "total": len(languages),
            "languages": languages,
            "default_language": "en"
        }
    except Exception as e:
        logger.error(f"Get languages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_languages.get("/stats")
async def get_language_stats() -> Dict[str, Any]:
    """Get translation statistics"""
    try:
        translator = get_translator()
        cache_stats = translator.get_cache_stats()
        lang_stats = translator.get_language_stats()
        
        return {
            "cache": cache_stats,
            "translation_paths": lang_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_languages.post("/cache/clear")
async def clear_translation_cache() -> Dict[str, Any]:
    """Clear translation cache"""
    try:
        translator = get_translator()
        translator.clear_cache()
        
        return {
            "status": "success",
            "message": "Translation cache cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Language Preference Endpoints
# ============================================================================

@router_preferences.post("/", response_model=LanguagePreferenceResponse)
async def set_language_preference(request: LanguagePreferenceRequest):
    """
    Set user's language preference
    
    - **user_id**: User ID
    - **primary_language**: Primary language code
    - **secondary_languages**: Secondary language codes
    - **auto_translate**: Enable auto-translation
    """
    try:
        translator = get_translator()
        pref = translator.set_user_preference(
            user_id=request.user_id,
            primary_language=request.primary_language,
            secondary_languages=request.secondary_languages,
            auto_translate=request.auto_translate
        )
        
        return LanguagePreferenceResponse(
            user_id=pref.user_id,
            primary_language=pref.primary_language,
            secondary_languages=pref.secondary_languages,
            auto_translate=pref.auto_translate,
            created_at=pref.created_at,
            updated_at=pref.updated_at
        )
    except Exception as e:
        logger.error(f"Set preference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_preferences.get("/{user_id}", response_model=LanguagePreferenceResponse)
async def get_language_preference(user_id: str):
    """
    Get user's language preference
    
    - **user_id**: User ID
    """
    try:
        translator = get_translator()
        pref = translator.get_user_preference(user_id)
        
        if not pref:
            # Return default preference
            pref = translator.set_user_preference(user_id)
        
        return LanguagePreferenceResponse(
            user_id=pref.user_id,
            primary_language=pref.primary_language,
            secondary_languages=pref.secondary_languages,
            auto_translate=pref.auto_translate,
            created_at=pref.created_at,
            updated_at=pref.updated_at
        )
    except Exception as e:
        logger.error(f"Get preference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_preferences.put("/{user_id}", response_model=LanguagePreferenceResponse)
async def update_language_preference(
    user_id: str,
    request: LanguagePreferenceRequest
):
    """
    Update user's language preference
    
    - **user_id**: User ID
    - **primary_language**: Primary language code
    - **secondary_languages**: Secondary language codes
    - **auto_translate**: Enable auto-translation
    """
    try:
        translator = get_translator()
        pref = translator.set_user_preference(
            user_id=user_id,
            primary_language=request.primary_language,
            secondary_languages=request.secondary_languages,
            auto_translate=request.auto_translate
        )
        
        return LanguagePreferenceResponse(
            user_id=pref.user_id,
            primary_language=pref.primary_language,
            secondary_languages=pref.secondary_languages,
            auto_translate=pref.auto_translate,
            created_at=pref.created_at,
            updated_at=pref.updated_at
        )
    except Exception as e:
        logger.error(f"Update preference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_preferences.delete("/{user_id}")
async def delete_language_preference(user_id: str) -> Dict[str, Any]:
    """
    Delete user's language preference (reset to default)
    
    - **user_id**: User ID
    """
    try:
        translator = get_translator()
        translator.set_user_preference(user_id, primary_language="en")
        
        return {
            "status": "success",
            "message": f"Language preference reset for user {user_id}",
            "default_language": "en"
        }
    except Exception as e:
        logger.error(f"Delete preference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Content Translation Endpoints (for Music, Movies, Videos, etc.)
# ============================================================================

router_content = APIRouter(prefix="/api/translate-content", tags=["Content Translation"])


class ContentTranslationRequest(BaseModel):
    """Request to translate content fields"""
    content: Dict[str, Any] = Field(..., description="Content object")
    source_language: str = Field(default="en", description="Source language")
    target_language: str = Field(default="en", description="Target language")
    fields_to_translate: List[str] = Field(
        default=["title", "description", "tags", "caption"],
        description="Fields to translate"
    )


@router_content.post("/music")
async def translate_music_content(request: ContentTranslationRequest) -> Dict[str, Any]:
    """Translate music content (title, description, etc.)"""
    try:
        translator = get_translator()
        result = translator.translate_content_for_platform(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language,
            fields_to_translate=request.fields_to_translate
        )
        
        return {
            "status": "success",
            "content_type": "music",
            "translated_content": result
        }
    except Exception as e:
        logger.error(f"Music content translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_content.post("/movies")
async def translate_movie_content(request: ContentTranslationRequest) -> Dict[str, Any]:
    """Translate movie content (title, description, etc.)"""
    try:
        translator = get_translator()
        result = translator.translate_content_for_platform(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language,
            fields_to_translate=request.fields_to_translate
        )
        
        return {
            "status": "success",
            "content_type": "movies",
            "translated_content": result
        }
    except Exception as e:
        logger.error(f"Movie content translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_content.post("/videos")
async def translate_video_content(request: ContentTranslationRequest) -> Dict[str, Any]:
    """Translate video content (title, description, etc.)"""
    try:
        translator = get_translator()
        result = translator.translate_content_for_platform(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language,
            fields_to_translate=request.fields_to_translate
        )
        
        return {
            "status": "success",
            "content_type": "videos",
            "translated_content": result
        }
    except Exception as e:
        logger.error(f"Video content translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_content.post("/chat")
async def translate_chat_message(request: ContentTranslationRequest) -> Dict[str, Any]:
    """Translate chat message"""
    try:
        translator = get_translator()
        result = translator.translate_content_for_platform(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language,
            fields_to_translate=["message", "text"]
        )
        
        return {
            "status": "success",
            "content_type": "chat",
            "translated_content": result
        }
    except Exception as e:
        logger.error(f"Chat translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
