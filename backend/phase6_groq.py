"""Phase 6+: Groq Integration for Copyright Detection"""
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


class GroqCopyrightChecker:
    """Groq-powered copyright detection"""
    
    def __init__(self, api_key: Optional[str] = None):
        if Groq:
            self.client = Groq(api_key=api_key) if api_key else Groq()
        else:
            self.client = None
        self.cache = {}
    
    async def check_track(self, title: str, artist: str) -> Tuple[bool, float]:
        """Check if track is likely copyrighted"""
        if not self.client:
            return False, 0.5
        
        try:
            prompt = f"Is '{title}' by {artist} likely copyrighted? Reply ONLY with: yes/no and 0.0-1.0 confidence"
            msg = self.client.messages.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            resp = msg.choices[0].message.content.lower()
            is_copy = "yes" in resp
            conf = 0.85 if is_copy else 0.15
            return is_copy, conf
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return False, 0.5
    
    def assess_claim(self, claim_data: Dict) -> Dict:
        """Assess copyright claim validity"""
        if not self.client:
            return {"validity": "unknown"}
        
        try:
            prompt = f"Rate claim validity (strong/moderate/weak): {json.dumps(claim_data)}"
            msg = self.client.messages.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30
            )
            return {"validity": msg.choices[0].message.content}
        except Exception as e:
            logger.error(f"Assessment error: {e}")
            return {"validity": "error"}
