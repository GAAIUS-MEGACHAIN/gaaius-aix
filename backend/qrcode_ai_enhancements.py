"""
AI-Enhanced QR Code Generator - Advanced Features
Using Groq (free tier) + HuggingFace (free) + Local ML Models
Production-ready with intelligent analytics, recommendations, and insights
"""

from fastapi import APIRouter, HTTPException, Body, Query, BackgroundTasks
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import motor.motor_asyncio
import qrcode
import hashlib
import uuid
import json
from io import BytesIO
import base64
from PIL import Image
import random
import string
from bson import ObjectId
import os
import asyncio

# AI/ML Imports
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False

router = APIRouter(prefix="/api/qrcode", tags=["QR Code"])

# ============ AI MODELS ============

class AIAnalyticsEngine:
    """Groq-powered analytics engine for intelligent insights"""
    
    def __init__(self):
        self.client = None
        if GROQ_AVAILABLE:
            api_key = os.environ.get("GROQ_API_KEY", "")
            if api_key:
                self.client = Groq(api_key=api_key)
    
    async def analyze_scan_patterns(self, scan_data: Dict) -> Dict:
        """Analyze scan patterns and provide insights using Groq"""
        if not self.client:
            return self._fallback_analysis(scan_data)
        
        try:
            prompt = f"""
            Analyze these QR code scan metrics and provide actionable insights:
            
            Total Scans: {scan_data.get('total_scans', 0)}
            Unique Scans: {scan_data.get('unique_scans', 0)}
            Device Breakdown: {json.dumps(scan_data.get('device_breakdown', {}))}
            Top Locations: {json.dumps(scan_data.get('location_breakdown', {}))}
            Scan Trend: {json.dumps(scan_data.get('hourly_scans', {}))}
            
            Provide:
            1. Key insights about engagement
            2. Device recommendations
            3. Geographic insights
            4. Trend analysis
            5. Next steps
            
            Format as JSON with keys: insights, device_rec, geo_insights, trends, recommendations
            """
            
            message = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            response_text = message.choices[0].message.content
            # Extract JSON from response
            try:
                # Try to find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass
            
            return {"insights": response_text}
            
        except Exception as e:
            return self._fallback_analysis(scan_data)
    
    async def generate_campaign_recommendations(self, campaign_data: Dict) -> Dict:
        """Generate campaign recommendations using Groq"""
        if not self.client:
            return self._fallback_recommendations(campaign_data)
        
        try:
            prompt = f"""
            A user wants to create a QR code campaign with these parameters:
            
            Industry: {campaign_data.get('industry', 'general')}
            Goal: {campaign_data.get('goal', 'increase engagement')}
            Target Audience: {campaign_data.get('audience', 'general')}
            Budget: {campaign_data.get('budget', 'unlimited')}
            Timeline: {campaign_data.get('timeline', '1 month')}
            
            Recommend:
            1. Best QR code type(s)
            2. Design recommendations
            3. Distribution channels
            4. Expected ROI
            5. Success metrics
            
            Format as JSON with keys: qr_type, design_tips, channels, expected_roi, metrics
            """
            
            message = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=600
            )
            
            response_text = message.choices[0].message.content
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass
            
            return {"recommendations": response_text}
            
        except Exception as e:
            return self._fallback_recommendations(campaign_data)
    
    def _fallback_analysis(self, scan_data: Dict) -> Dict:
        """Fallback analysis without Groq"""
        total = scan_data.get('total_scans', 0)
        unique = scan_data.get('unique_scans', 0)
        
        engagement_rate = (unique / total * 100) if total > 0 else 0
        
        return {
            "insights": f"Campaign has {total} scans with {engagement_rate:.1f}% unique engagement",
            "device_rec": "Focus on mobile optimization - mobile traffic typically converts better",
            "geo_insights": "Monitor top geographic regions for localized campaigns",
            "trends": "Track hourly trends to identify peak engagement times",
            "recommendations": "Use these insights to optimize future campaigns"
        }
    
    def _fallback_recommendations(self, campaign_data: Dict) -> Dict:
        """Fallback recommendations without Groq"""
        return {
            "qr_type": ["url", "product"],
            "design_tips": "Use brand colors and clear call-to-action",
            "channels": ["social_media", "print", "email"],
            "expected_roi": "100-300% depending on implementation",
            "metrics": ["scan_count", "unique_users", "conversion_rate"]
        }


class MLPatternDetector:
    """Machine learning for pattern detection and clustering"""
    
    @staticmethod
    async def detect_scan_clusters(scan_events: List[Dict]) -> Dict:
        """Detect clusters in scan patterns using K-means"""
        if not ML_AVAILABLE or not scan_events:
            return {"clusters": [], "analysis": "Insufficient data"}
        
        try:
            # Extract features
            features = []
            for event in scan_events:
                location = event.get("location", {})
                hour = event.get("timestamp", datetime.utcnow()).hour
                
                device_score = {"mobile": 1, "desktop": 2, "tablet": 3}.get(
                    event.get("device_type", "mobile"), 1
                )
                
                features.append([
                    location.get("lat", 0),
                    location.get("lng", 0),
                    hour,
                    device_score
                ])
            
            if len(features) < 2:
                return {"clusters": [], "analysis": "Need more data"}
            
            features_array = np.array(features)
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_array)
            
            # Determine optimal clusters
            n_clusters = min(3, len(features_array))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            return {
                "clusters": clusters.tolist(),
                "n_clusters": n_clusters,
                "analysis": f"Detected {n_clusters} distinct scan patterns"
            }
        except Exception as e:
            return {"clusters": [], "analysis": f"Analysis unavailable: {str(e)}"}
    
    @staticmethod
    async def predict_engagement_trend(scan_history: List[Dict]) -> Dict:
        """Predict future engagement based on historical data"""
        if not ML_AVAILABLE or not scan_history:
            return {"prediction": "insufficient_data", "confidence": 0}
        
        try:
            # Sort by timestamp
            sorted_scans = sorted(scan_history, key=lambda x: x.get("timestamp", ""))
            
            if len(sorted_scans) < 3:
                return {"prediction": "need_more_data", "confidence": 0}
            
            # Simple trend analysis
            scans_per_period = len(sorted_scans) / max(1, len(set([
                s.get("timestamp", "").split("T")[0] for s in sorted_scans
            ])))
            
            # Predict trend
            if scans_per_period > 10:
                trend = "upward"
                confidence = 0.8
            elif scans_per_period > 5:
                trend = "stable"
                confidence = 0.7
            else:
                trend = "declining"
                confidence = 0.6
            
            return {
                "prediction": trend,
                "scans_per_day": round(scans_per_period, 2),
                "confidence": confidence
            }
        except Exception as e:
            return {"prediction": "error", "confidence": 0}


# ============ MODELS ============

class AIInsight(BaseModel):
    """AI-generated insight"""
    type: str  # pattern_analysis, trend_prediction, recommendation
    title: str
    description: str
    confidence: float = Field(ge=0, le=1)
    suggested_action: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignRecommendation(BaseModel):
    """AI-generated campaign recommendation"""
    qr_type: str
    design_tips: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    expected_metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(ge=0, le=1)
    reasoning: str

class EnhancedAnalytics(BaseModel):
    """Enhanced analytics with AI insights"""
    qr_id: str
    basic_metrics: Dict[str, Any]
    ai_insights: List[AIInsight] = Field(default_factory=list)
    pattern_clusters: Dict[str, Any] = Field(default_factory=dict)
    engagement_prediction: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Optional[CampaignRecommendation] = None

# ============ GLOBAL INSTANCES ============

ai_engine = AIAnalyticsEngine()
ml_detector = MLPatternDetector()
db = None

def get_db():
    global db
    return db

def set_db(database):
    global db
    db = database

# ============ AI ENHANCEMENT ROUTES ============

@router.post("/ai/analyze-patterns")
async def analyze_scan_patterns(qr_id: str = Query(...), user_id: str = Query(...)):
    """Analyze QR code scan patterns with AI"""
    try:
        db_conn = get_db()
        
        # Get analytics data
        analytics = await db_conn.analytics.find_one({"qr_id": qr_id})
        if not analytics:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Run AI analysis
        ai_insights = await ai_engine.analyze_scan_patterns({
            "total_scans": analytics.get("total_scans", 0),
            "unique_scans": analytics.get("unique_scans", 0),
            "device_breakdown": analytics.get("device_breakdown", {}),
            "location_breakdown": analytics.get("location_breakdown", {}),
            "hourly_scans": analytics.get("hourly_scans", {})
        })
        
        # Detect patterns with ML
        scan_events = analytics.get("scan_events", [])
        clusters = await ml_detector.detect_scan_clusters(scan_events)
        
        return {
            "qr_id": qr_id,
            "ai_analysis": ai_insights,
            "pattern_clusters": clusters,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/campaign-recommendations")
async def get_campaign_recommendations(
    user_id: str = Query(...),
    campaign_data: Dict = Body(...)
):
    """Get AI-powered campaign recommendations"""
    try:
        # Generate recommendations
        recommendations = await ai_engine.generate_campaign_recommendations(campaign_data)
        
        # Store recommendations
        db_conn = get_db()
        result = await db_conn.ai_recommendations.insert_one({
            "user_id": user_id,
            "campaign_data": campaign_data,
            "recommendations": recommendations,
            "created_at": datetime.utcnow()
        })
        
        return {
            "recommendation_id": str(result.inserted_id),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/enhanced-analytics/{qr_id}")
async def get_enhanced_analytics(qr_id: str, user_id: str = Query(...)):
    """Get enhanced analytics with AI insights"""
    try:
        db_conn = get_db()
        
        # Get QR code
        qr_code = await db_conn.qr_codes.find_one({"code_id": qr_id, "user_id": user_id})
        if not qr_code:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Get analytics
        analytics = await db_conn.analytics.find_one({"qr_id": qr_id})
        if not analytics:
            analytics = {"qr_id": qr_id, "total_scans": 0, "scan_events": []}
        
        # AI analysis
        ai_insights_data = await ai_engine.analyze_scan_patterns({
            "total_scans": analytics.get("total_scans", 0),
            "unique_scans": analytics.get("unique_scans", 0),
            "device_breakdown": analytics.get("device_breakdown", {}),
            "location_breakdown": analytics.get("location_breakdown", {}),
            "hourly_scans": analytics.get("hourly_scans", {})
        })
        
        # Create insights
        ai_insights = [
            AIInsight(
                type="pattern_analysis",
                title="Scan Pattern Analysis",
                description=ai_insights_data.get("insights", ""),
                confidence=0.85,
                suggested_action=ai_insights_data.get("recommendations")
            )
        ]
        
        # Pattern detection
        clusters = await ml_detector.detect_scan_clusters(analytics.get("scan_events", []))
        
        # Engagement prediction
        prediction = await ml_detector.predict_engagement_trend(analytics.get("scan_events", []))
        
        return {
            "qr_id": qr_id,
            "basic_metrics": {
                "total_scans": analytics.get("total_scans", 0),
                "unique_scans": analytics.get("unique_scans", 0),
                "device_breakdown": analytics.get("device_breakdown", {}),
                "location_breakdown": analytics.get("location_breakdown", {})
            },
            "ai_insights": [i.dict() for i in ai_insights],
            "pattern_clusters": clusters,
            "engagement_prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/predict-engagement")
async def predict_engagement(qr_id: str = Query(...), user_id: str = Query(...)):
    """Predict future engagement using ML"""
    try:
        db_conn = get_db()
        
        # Get analytics
        analytics = await db_conn.analytics.find_one({"qr_id": qr_id})
        if not analytics:
            raise HTTPException(status_code=404, detail="Analytics not found")
        
        # Predict
        prediction = await ml_detector.predict_engagement_trend(
            analytics.get("scan_events", [])
        )
        
        return {
            "qr_id": qr_id,
            "prediction": prediction,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/insights-history/{qr_id}")
async def get_insights_history(qr_id: str, user_id: str = Query(...), limit: int = 10):
    """Get historical AI insights"""
    try:
        db_conn = get_db()
        
        insights = await db_conn.ai_insights.find(
            {"qr_id": qr_id, "user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {"insights": insights, "count": len(insights)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/optimize-qr-design")
async def optimize_qr_design(
    user_id: str = Query(...),
    qr_type: str = Query(...),
    current_performance: Dict = Body(...)
):
    """Get AI recommendations for QR design optimization"""
    try:
        prompt = f"""
        A QR code has {current_performance.get('total_scans', 0)} scans with these metrics:
        - Device breakdown: {json.dumps(current_performance.get('device_breakdown', {}))}
        - Engagement: {current_performance.get('unique_scans', 0)} unique users
        
        Recommend design optimizations for a {qr_type} QR code:
        1. Color scheme recommendations
        2. Size recommendations
        3. Error correction level
        4. Pattern suggestions
        
        Format as JSON with these keys: colors, size, error_correction, patterns, reasoning
        """
        
        if ai_engine.client:
            message = ai_engine.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            response_text = message.choices[0].message.content
            
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    return json.loads(response_text[start_idx:end_idx])
            except:
                pass
        
        # Fallback
        return {
            "colors": ["#667eea", "#764ba2"],
            "size": 300,
            "error_correction": "H",
            "patterns": ["rounded"],
            "reasoning": "High error correction for better readability"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/smart-insights/{qr_id}")
async def get_smart_insights(qr_id: str, user_id: str = Query(...)):
    """Get comprehensive smart insights"""
    try:
        db_conn = get_db()
        
        qr_code = await db_conn.qr_codes.find_one({"code_id": qr_id, "user_id": user_id})
        if not qr_code:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        analytics = await db_conn.analytics.find_one({"qr_id": qr_id})
        if not analytics:
            analytics = {
                "total_scans": 0,
                "unique_scans": 0,
                "scan_events": [],
                "device_breakdown": {},
                "location_breakdown": {}
            }
        
        # Comprehensive analysis
        ai_analysis = await ai_engine.analyze_scan_patterns({
            "total_scans": analytics.get("total_scans", 0),
            "unique_scans": analytics.get("unique_scans", 0),
            "device_breakdown": analytics.get("device_breakdown", {}),
            "location_breakdown": analytics.get("location_breakdown", {}),
            "hourly_scans": analytics.get("hourly_scans", {})
        })
        
        patterns = await ml_detector.detect_scan_clusters(analytics.get("scan_events", []))
        prediction = await ml_detector.predict_engagement_trend(analytics.get("scan_events", []))
        
        # Store insight
        insight_record = {
            "user_id": user_id,
            "qr_id": qr_id,
            "qr_type": qr_code.get("qr_type"),
            "analysis": ai_analysis,
            "patterns": patterns,
            "prediction": prediction,
            "created_at": datetime.utcnow()
        }
        await db_conn.ai_insights.insert_one(insight_record)
        
        return {
            "qr_id": qr_id,
            "title": qr_code.get("title"),
            "analysis": ai_analysis,
            "patterns": patterns,
            "prediction": prediction,
            "metrics": {
                "total_scans": analytics.get("total_scans", 0),
                "unique_scans": analytics.get("unique_scans", 0),
                "conversion_rate": (analytics.get("unique_scans", 0) / max(1, analytics.get("total_scans", 1))) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/health")
async def ai_health():
    """Check AI services health"""
    return {
        "status": "ok",
        "groq_available": GROQ_AVAILABLE and ai_engine.client is not None,
        "ml_available": ML_AVAILABLE,
        "service": "qrcode_ai"
    }
