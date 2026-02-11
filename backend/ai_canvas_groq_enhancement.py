"""
AI Canvas Groq Enhancement Service
Uses Groq API (free tier) for AI-powered design suggestions and content generation
Groq provides extremely fast inference for LLaMA and other models
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import asyncio
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Groq API integration (free tier available)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq not installed. Install with: pip install groq")

class DesignPrompt(BaseModel):
    """AI design suggestion request"""
    category: str  # social_media, business, event, etc.
    purpose: str  # What is this design for?
    style: Optional[str] = None  # minimal, bold, elegant, modern
    audience: Optional[str] = None  # target audience
    brand_colors: Optional[List[str]] = None
    additional_context: Optional[str] = None

class ContentSuggestion(BaseModel):
    """AI content suggestion"""
    text_type: str  # headline, description, call_to_action, etc.
    topic: str
    tone: str = "professional"  # professional, casual, funny, inspirational
    length: str = "medium"  # short, medium, long
    context: Optional[str] = None

class DesignAssistant:
    """AI-powered design assistant using Groq"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key and GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
            logger.info("✅ Groq AI Enhancement initialized")
        else:
            logger.warning("⚠️ Groq AI not configured. Set GROQ_API_KEY environment variable")

    async def generate_design_suggestions(self, prompt: DesignPrompt) -> Dict[str, Any]:
        """Generate AI-powered design suggestions"""
        if not self.client:
            return {"error": "Groq AI not configured", "suggestions": self._get_fallback_suggestions(prompt)}

        try:
            system_prompt = """You are an expert graphic designer and design consultant. 
            Provide practical, actionable design suggestions for creating beautiful, effective designs.
            Focus on: layout, color theory, typography, composition, and best practices.
            Be specific and detailed in your recommendations."""

            user_prompt = f"""Design Brief:
Category: {prompt.category}
Purpose: {prompt.purpose}
Style Preference: {prompt.style or 'any modern style'}
Target Audience: {prompt.audience or 'general'}
Brand Colors: {prompt.brand_colors or 'not specified'}
Additional Context: {prompt.additional_context or 'none'}

Please provide 5 specific design suggestions for this project, including:
1. Layout and composition recommendations
2. Color scheme suggestions
3. Typography recommendations
4. Visual elements to include
5. Best practices for this type of design

Format as JSON with keys: layout, colors, typography, elements, best_practices"""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",  # Free model on Groq
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            suggestions_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                suggestions = json.loads(suggestions_text)
            except:
                suggestions = {"recommendations": suggestions_text}

            return {
                "success": True,
                "suggestions": suggestions,
                "model": "mixtral-8x7b-32768",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Groq design suggestion error: {e}")
            return {"error": str(e), "suggestions": self._get_fallback_suggestions(prompt)}

    async def generate_content(self, prompt: ContentSuggestion) -> Dict[str, str]:
        """Generate AI-powered content suggestions"""
        if not self.client:
            return {"error": "Groq AI not configured", "content": self._get_fallback_content(prompt)}

        try:
            system_prompt = f"""You are a professional copywriter and content strategist.
            Generate compelling, engaging content that resonates with the audience.
            Tone: {prompt.tone}
            Length: {prompt.length}
            Be creative, specific, and actionable."""

            user_prompt = f"""Generate 3 {prompt.text_type} variations for:
Topic: {prompt.topic}
Target Tone: {prompt.tone}
Length: {prompt.length}
Context: {prompt.context or 'general use'}

For each variation, provide the content and explain why it works.
Format as JSON with keys: variation1, variation2, variation3"""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )

            content_text = response.choices[0].message.content

            try:
                content = json.loads(content_text)
            except:
                content = {"variations": content_text}

            return {
                "success": True,
                "content": content,
                "model": "mixtral-8x7b-32768",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Groq content generation error: {e}")
            return {"error": str(e), "content": self._get_fallback_content(prompt)}

    async def get_design_inspiration(self, category: str) -> Dict[str, Any]:
        """Get design inspiration and trends for a category"""
        if not self.client:
            return {"error": "Groq AI not configured", "inspiration": {}}

        try:
            prompt = f"""Provide current design trends and inspiration for {category} designs.
            Include:
            1. Current trending styles
            2. Popular color palettes
            3. Recommended fonts/typography
            4. Composition patterns
            5. Design do's and don'ts
            
            Format as JSON."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            inspiration_text = response.choices[0].message.content

            try:
                inspiration = json.loads(inspiration_text)
            except:
                inspiration = {"trends": inspiration_text}

            return {
                "success": True,
                "inspiration": inspiration,
                "category": category,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Groq inspiration error: {e}")
            return {"error": str(e), "inspiration": {}}

    def _get_fallback_suggestions(self, prompt: DesignPrompt) -> Dict[str, str]:
        """Fallback suggestions when Groq is unavailable"""
        fallback = {
            "layout": "Use a clean grid layout with plenty of white space",
            "colors": "Choose 2-3 complementary colors from your brand palette",
            "typography": "Use sans-serif fonts for headings and body text for readability",
            "elements": f"Include relevant imagery for {prompt.purpose}",
            "best_practices": "Maintain visual hierarchy, ensure mobile responsiveness, test on multiple devices"
        }
        return fallback

    def _get_fallback_content(self, prompt: ContentSuggestion) -> Dict[str, str]:
        """Fallback content when Groq is unavailable"""
        return {
            "variation1": f"Create engaging {prompt.text_type} about {prompt.topic}",
            "variation2": f"Make your {prompt.text_type} stand out for {prompt.topic}",
            "variation3": f"Try this {prompt.text_type} approach for {prompt.topic}"
        }

# Global design assistant instance
design_assistant = DesignAssistant()

# API Routes
router = APIRouter(prefix="/api/ai-canvas/design-ai", tags=["Design AI Enhancement"])

@router.post("/suggestions")
async def get_design_suggestions(prompt: DesignPrompt):
    """Get AI-powered design suggestions using Groq"""
    return await design_assistant.generate_design_suggestions(prompt)

@router.post("/content")
async def generate_content(prompt: ContentSuggestion):
    """Generate AI-powered content suggestions"""
    return await design_assistant.generate_content(prompt)

@router.get("/inspiration/{category}")
async def get_inspiration(category: str):
    """Get design inspiration for a category"""
    return await design_assistant.get_design_inspiration(category)

@router.post("/brainstorm")
async def brainstorm_designs(
    topic: str = Body(...),
    industry: Optional[str] = Body(None),
    count: int = Body(5, ge=1, le=10)
):
    """Brainstorm design ideas for a topic"""
    if not design_assistant.client:
        return {"error": "Groq AI not configured"}

    try:
        prompt = f"""Generate {count} creative design ideas for:
Topic: {topic}
Industry: {industry or 'general'}

For each idea, provide:
- Concept name
- Description
- Key design elements
- Target audience
- Why it works

Format as JSON list."""

        response = await asyncio.to_thread(
            design_assistant.client.chat.completions.create,
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=2000
        )

        ideas_text = response.choices[0].message.content

        try:
            ideas = json.loads(ideas_text)
        except:
            ideas = {"brainstorm": ideas_text}

        return {
            "success": True,
            "ideas": ideas,
            "count": count,
            "topic": topic,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Brainstorm error: {e}")
        return {"error": str(e)}
