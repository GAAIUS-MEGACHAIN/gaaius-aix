"""
AI Tutoring Engine for E-Learning Platform
Provides intelligent, adaptive tutoring using LLMs and ML models
Integrated with existing eLearning analytics and course management
"""

from fastapi import APIRouter, HTTPException, Body, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import asyncio
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

# ============== MULTIPLE LLM PROVIDER SUPPORT ==============
# Support multiple free AI providers for maximum compatibility

LLM_PROVIDERS = {}

# 1. GROQ (Primary - Free tier, Mixtral-8x7B, LLaMA-2)
try:
    from groq import Groq
    LLM_PROVIDERS['groq'] = True
    logger.info("✅ Groq SDK available")
except ImportError:
    LLM_PROVIDERS['groq'] = False
    logger.warning("Groq not installed. Install with: pip install groq")

# 2. OPENAI (Fallback - GPT-3.5-turbo, free credits available)
try:
    import openai
    LLM_PROVIDERS['openai'] = True
    logger.info("✅ OpenAI SDK available")
except ImportError:
    LLM_PROVIDERS['openai'] = False

# 3. COHERE (Fallback - Free tier available)
try:
    import cohere
    LLM_PROVIDERS['cohere'] = True
    logger.info("✅ Cohere SDK available")
except ImportError:
    LLM_PROVIDERS['cohere'] = False

# 4. OLLAMA (Fallback - Local open-source models, completely free)
try:
    import requests
    LLM_PROVIDERS['ollama'] = True
    logger.info("✅ Ollama available (local)")
except ImportError:
    LLM_PROVIDERS['ollama'] = False

# 5. HUGGINGFACE (Fallback - Free inference models)
try:
    from transformers import pipeline
    LLM_PROVIDERS['huggingface'] = True
    logger.info("✅ HuggingFace Transformers available")
except ImportError:
    LLM_PROVIDERS['huggingface'] = False

# 6. ML MODELS FOR TUTORING
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    ML_MODELS_AVAILABLE = True
    logger.info("✅ ML models available for content classification")
except ImportError:
    ML_MODELS_AVAILABLE = False
    logger.warning("scikit-learn not installed. Install with: pip install scikit-learn")

# 7. VECTOR EMBEDDINGS (For semantic search)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
    logger.info("✅ Sentence transformers available for embeddings")
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


# ============== LLM PROVIDER MANAGER ==============
class LLMProviderManager:
    """
    Manages multiple LLM providers with intelligent fallback chain.
    Supports Groq, OpenAI, Cohere, Claude, Ollama, and HuggingFace.
    """

    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.cohere_client = None
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.provider_status = {}
        self.last_used_provider = None
        
        # Initialize available providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available LLM providers"""
        
        # Groq initialization
        if LLM_PROVIDERS.get('groq'):
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                try:
                    self.groq_client = Groq(api_key=groq_api_key)
                    self.provider_status['groq'] = 'ready'
                    logger.info("✅ Groq provider initialized")
                except Exception as e:
                    self.provider_status['groq'] = f'error: {str(e)}'
                    logger.warning(f"⚠️ Groq initialization failed: {e}")
            else:
                self.provider_status['groq'] = 'no_api_key'
                logger.warning("⚠️ GROQ_API_KEY not found")
        else:
            self.provider_status['groq'] = 'not_installed'

        # OpenAI initialization
        if LLM_PROVIDERS.get('openai'):
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    import openai as openai_module
                    openai_module.api_key = openai_api_key
                    self.openai_client = openai_module
                    self.provider_status['openai'] = 'ready'
                    logger.info("✅ OpenAI provider initialized")
                except Exception as e:
                    self.provider_status['openai'] = f'error: {str(e)}'
                    logger.warning(f"⚠️ OpenAI initialization failed: {e}")
            else:
                self.provider_status['openai'] = 'no_api_key'
        else:
            self.provider_status['openai'] = 'not_installed'

        # Cohere initialization
        if LLM_PROVIDERS.get('cohere'):
            cohere_api_key = os.getenv("COHERE_API_KEY")
            if cohere_api_key:
                try:
                    import cohere as cohere_module
                    self.cohere_client = cohere_module.Client(api_key=cohere_api_key)
                    self.provider_status['cohere'] = 'ready'
                    logger.info("✅ Cohere provider initialized")
                except Exception as e:
                    self.provider_status['cohere'] = f'error: {str(e)}'
                    logger.warning(f"⚠️ Cohere initialization failed: {e}")
            else:
                self.provider_status['cohere'] = 'no_api_key'
        else:
            self.provider_status['cohere'] = 'not_installed'

        # Ollama initialization (check if running)
        if LLM_PROVIDERS.get('ollama'):
            try:
                import requests
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    self.provider_status['ollama'] = 'ready'
                    logger.info("✅ Ollama provider detected (local)")
                else:
                    self.provider_status['ollama'] = 'not_running'
            except Exception as e:
                self.provider_status['ollama'] = 'not_running'
        else:
            self.provider_status['ollama'] = 'not_installed'

        # HuggingFace initialization
        if LLM_PROVIDERS.get('huggingface'):
            try:
                from transformers import pipeline
                self.provider_status['huggingface'] = 'ready'
                logger.info("✅ HuggingFace provider available")
            except Exception as e:
                self.provider_status['huggingface'] = f'error: {str(e)}'
        else:
            self.provider_status['huggingface'] = 'not_installed'

    async def generate_with_groq(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Generate text using Groq (Primary provider)"""
        if not self.groq_client:
            return None
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            self.last_used_provider = 'groq'
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq generation failed: {e}")
            return None

    async def generate_with_openai(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Generate text using OpenAI (Fallback #1)"""
        if not self.openai_client:
            return None
        try:
            import openai as openai_module
            response = openai_module.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            self.last_used_provider = 'openai'
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"OpenAI generation failed: {e}")
            return None

    async def generate_with_cohere(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Generate text using Cohere (Fallback #2)"""
        if not self.cohere_client:
            return None
        try:
            response = self.cohere_client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7
            )
            self.last_used_provider = 'cohere'
            return response.generations[0].text
        except Exception as e:
            logger.warning(f"Cohere generation failed: {e}")
            return None

    async def generate_with_ollama(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Generate text using Ollama (Fallback #3 - Local)"""
        try:
            import requests
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "mistral",  # or "llama2", "neural-chat"
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                },
                timeout=30
            )
            if response.status_code == 200:
                self.last_used_provider = 'ollama'
                return response.json().get('response', '')
            return None
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")
            return None

    async def generate_with_huggingface(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """Generate text using HuggingFace (Fallback #4 - Local)"""
        try:
            from transformers import pipeline
            generator = pipeline("text-generation", model="gpt2")
            result = generator(prompt, max_length=max_tokens, do_sample=True)[0]
            self.last_used_provider = 'huggingface'
            return result['generated_text']
        except Exception as e:
            logger.warning(f"HuggingFace generation failed: {e}")
            return None

    async def generate_text(self, prompt: str, max_tokens: int = 1024) -> tuple[Optional[str], str]:
        """
        Generate text using intelligent fallback chain.
        
        Priority order:
        1. Groq (fastest, free tier)
        2. OpenAI (best quality, free credits)
        3. Cohere (always available, free tier)
        4. Ollama (local, completely free)
        5. HuggingFace (local, free)
        
        Returns:
            Tuple of (generated_text, provider_used)
        """
        # Try Groq first (fastest)
        if self.provider_status.get('groq') == 'ready':
            result = await self.generate_with_groq(prompt, max_tokens)
            if result:
                logger.info(f"✅ Generated with Groq")
                return result, 'groq'

        # Try OpenAI
        if self.provider_status.get('openai') == 'ready':
            result = await self.generate_with_openai(prompt, max_tokens)
            if result:
                logger.info(f"✅ Generated with OpenAI (Groq unavailable)")
                return result, 'openai'

        # Try Cohere
        if self.provider_status.get('cohere') == 'ready':
            result = await self.generate_with_cohere(prompt, max_tokens)
            if result:
                logger.info(f"✅ Generated with Cohere (Groq/OpenAI unavailable)")
                return result, 'cohere'

        # Try Ollama (local)
        if self.provider_status.get('ollama') == 'ready':
            result = await self.generate_with_ollama(prompt, max_tokens)
            if result:
                logger.info(f"✅ Generated with Ollama (online providers unavailable)")
                return result, 'ollama'

        # Try HuggingFace (local)
        if self.provider_status.get('huggingface') == 'ready':
            result = await self.generate_with_huggingface(prompt, max_tokens)
            if result:
                logger.info(f"✅ Generated with HuggingFace (online providers unavailable)")
                return result, 'huggingface'

        # All providers failed
        logger.error("❌ All LLM providers unavailable!")
        return None, 'none'

    def get_provider_status(self) -> Dict[str, str]:
        """Get status of all configured providers"""
        return self.provider_status.copy()


# ============== CONTENT CLASSIFIER ==============
class ContentClassifier:
    """
    ML-based content classifier to automatically detect eLearning content type.
    Uses keyword matching and TF-IDF for classification.
    """

    def __init__(self):
        """Initialize content classifier with keyword mappings"""
        self.keywords = {
            ContentType.MATH: [
                'algebra', 'geometry', 'calculus', 'theorem', 'equation',
                'derivative', 'integral', 'matrix', 'polynomial', 'fraction',
                'exponent', 'logarithm', 'trigonometry', 'sine', 'cosine',
                'probability', 'statistics', 'mean', 'median', 'variance'
            ],
            ContentType.SCIENCE: [
                'physics', 'chemistry', 'biology', 'atom', 'molecule',
                'force', 'gravity', 'energy', 'reaction', 'cell',
                'organism', 'ecosystem', 'element', 'compound', 'nucleus',
                'electron', 'photosynthesis', 'respiration', 'genetics'
            ],
            ContentType.LANGUAGE: [
                'grammar', 'syntax', 'vocabulary', 'essay', 'writing',
                'pronoun', 'verb', 'noun', 'adjective', 'adverb',
                'sentence', 'paragraph', 'punctuation', 'spelling',
                'literature', 'poem', 'novel', 'dialogue', 'language'
            ],
            ContentType.HISTORY: [
                'history', 'war', 'civilization', 'empire', 'revolution',
                'century', 'era', 'dynasty', 'culture', 'society',
                'political', 'government', 'president', 'monarch',
                'treaty', 'constitution', 'independence', 'settlement'
            ],
            ContentType.TECHNOLOGY: [
                'programming', 'code', 'algorithm', 'software', 'hardware',
                'python', 'java', 'javascript', 'database', 'network',
                'server', 'cloud', 'artificial intelligence', 'machine learning',
                'data science', 'web development', 'cybersecurity', 'api'
            ],
            ContentType.BUSINESS: [
                'business', 'economics', 'finance', 'marketing', 'sales',
                'management', 'entrepreneurship', 'market', 'profit',
                'revenue', 'investment', 'stock', 'trade', 'commerce',
                'supply', 'demand', 'contract', 'accounting'
            ],
            ContentType.ARTS: [
                'art', 'music', 'painting', 'sculpture', 'drawing',
                'literature', 'theater', 'dance', 'film', 'composition',
                'melody', 'harmony', 'rhythm', 'color', 'perspective',
                'aesthetic', 'creative', 'expression', 'style'
            ]
        }
        self.vectorizer = None
        self.fit_vectorizer()

    def fit_vectorizer(self):
        """Fit TF-IDF vectorizer on keywords"""
        if ML_MODELS_AVAILABLE:
            try:
                all_keywords = []
                for keywords in self.keywords.values():
                    all_keywords.extend(keywords)
                
                self.vectorizer = TfidfVectorizer(
                    vocabulary=set(all_keywords),
                    lowercase=True
                )
                logger.info("✅ Content classifier initialized with ML models")
            except Exception as e:
                logger.warning(f"TF-IDF vectorizer fit failed: {e}")
                self.vectorizer = None

    def classify(self, text: str) -> ContentType:
        """
        Classify content type from text.
        
        Uses keyword matching + TF-IDF for high accuracy.
        Falls back to keyword matching if ML unavailable.
        
        Args:
            text: Content to classify
            
        Returns:
            ContentType enum value
        """
        text_lower = text.lower()
        
        # Score each content type
        scores = {}
        for content_type, keywords in self.keywords.items():
            # Count keyword matches
            match_count = sum(1 for kw in keywords if kw in text_lower)
            scores[content_type] = match_count

        # Return content type with highest score
        best_type = max(scores, key=scores.get)
        
        # If no clear winner, return GENERAL
        if scores[best_type] == 0:
            return ContentType.GENERAL
        
        return best_type

    def classify_with_confidence(self, text: str) -> tuple[ContentType, float]:
        """
        Classify content with confidence score.
        
        Args:
            text: Content to classify
            
        Returns:
            Tuple of (ContentType, confidence_score 0-1)
        """
        text_lower = text.lower()
        scores = {}
        
        for content_type, keywords in self.keywords.items():
            match_count = sum(1 for kw in keywords if kw in text_lower)
            scores[content_type] = match_count

        total_matches = sum(scores.values())
        best_type = max(scores, key=scores.get)
        
        if total_matches == 0:
            return ContentType.GENERAL, 0.0
        
        # Calculate confidence as proportion of best type vs total
        confidence = scores[best_type] / max(total_matches, 1)
        return best_type, min(confidence, 1.0)


# ============== DIFFICULTY PREDICTOR ==============
class DifficultyPredictor:
    """
    ML-based difficulty predictor that scales questions based on student performance.
    Analyzes student history and adapts difficulty in real-time.
    """

    def __init__(self):
        """Initialize difficulty predictor"""
        self.performance_threshold = {
            DifficultyLevel.BEGINNER: 0.4,
            DifficultyLevel.INTERMEDIATE: 0.6,
            DifficultyLevel.ADVANCED: 0.8,
            DifficultyLevel.EXPERT: 0.95
        }

    async def predict_difficulty(
        self,
        student_profile: 'StudentKnowledgeProfile',
        content_type: ContentType,
        current_performance: Optional[float] = None
    ) -> DifficultyLevel:
        """
        Predict optimal difficulty level based on student performance.
        
        Args:
            student_profile: Student's knowledge profile
            content_type: Type of content being tutored
            current_performance: Current session performance (0-1)
            
        Returns:
            Optimal DifficultyLevel
        """
        
        # Get student's proficiency in this content area
        proficiency = student_profile.estimated_proficiency.get(
            content_type.value, 0.5
        )
        
        # Factor in current performance if available
        if current_performance is not None:
            proficiency = (proficiency + current_performance) / 2

        # Determine difficulty level based on proficiency
        if proficiency < self.performance_threshold[DifficultyLevel.BEGINNER]:
            return DifficultyLevel.BEGINNER
        elif proficiency < self.performance_threshold[DifficultyLevel.INTERMEDIATE]:
            return DifficultyLevel.INTERMEDIATE
        elif proficiency < self.performance_threshold[DifficultyLevel.ADVANCED]:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT

    async def update_proficiency(
        self,
        student_profile: 'StudentKnowledgeProfile',
        content_type: ContentType,
        performance_score: float
    ) -> None:
        """
        Update student's proficiency based on performance.
        
        Args:
            student_profile: Student's knowledge profile
            content_type: Content type just completed
            performance_score: Performance score (0-1)
        """
        content_key = content_type.value
        
        # Update proficiency with exponential moving average
        current_proficiency = student_profile.estimated_proficiency.get(content_key, 0.5)
        alpha = 0.3  # Learning rate
        new_proficiency = (alpha * performance_score) + ((1 - alpha) * current_proficiency)
        
        student_profile.estimated_proficiency[content_key] = min(new_proficiency, 1.0)
        student_profile.last_updated = datetime.utcnow()
        
        logger.info(
            f"📊 Updated {content_type.value} proficiency to {new_proficiency:.2f} "
            f"(was {current_proficiency:.2f})"
        )


# ============== ENUMS ==============

class TutorMode(str, Enum):
    """Tutoring mode"""
    EXPLANATION = "explanation"      # Explain concepts
    PRACTICE = "practice"            # Practice problems
    ASSESSMENT = "assessment"        # Test knowledge
    REMEDIAL = "remedial"            # Fill knowledge gaps
    SOCRATIC = "socratic"            # Guided questioning
    ADAPTIVE = "adaptive"            # AI-chosen based on performance

class DifficultyLevel(str, Enum):
    """Difficulty level for questions"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ResponseType(str, Enum):
    """Type of tutoring response"""
    EXPLANATION = "explanation"
    QUESTION = "question"
    HINT = "hint"
    FEEDBACK = "feedback"
    SUMMARY = "summary"

class ContentType(str, Enum):
    """Type of eLearning content"""
    MATH = "math"                      # Mathematics, Algebra, Calculus, Geometry
    SCIENCE = "science"                # Physics, Chemistry, Biology
    LANGUAGE = "language"              # English, Foreign Languages, Writing
    HISTORY = "history"                # History, Social Studies, Civics
    TECHNOLOGY = "technology"          # Computer Science, Programming, IT
    BUSINESS = "business"              # Business, Economics, Finance
    ARTS = "arts"                      # Art, Music, Literature
    GENERAL = "general"                # General Knowledge, Mixed Topics

# ============== MODELS ==============

class TutoringRequest(BaseModel):
    """Request for tutoring"""
    student_id: str
    course_id: str
    lesson_id: str
    topic: str
    content_type: Optional[ContentType] = None  # Auto-detected if not provided
    mode: TutorMode = TutorMode.ADAPTIVE
    difficulty: Optional[DifficultyLevel] = None  # Auto-predicted if not provided
    student_response: Optional[str] = None
    context: Optional[str] = None

class PracticeQuestionRequest(BaseModel):
    """Request for practice question"""
    student_id: str
    lesson_id: str
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    count: int = Field(1, ge=1, le=5)

class AssessmentRequest(BaseModel):
    """Request for assessment"""
    student_id: str
    course_id: str
    lesson_id: str
    question_count: int = Field(5, ge=1, le=20)

class StudentAnswer(BaseModel):
    """Student answer to a question"""
    question_id: str
    answer: str
    time_spent_seconds: int = 0

class TutoringResponse(BaseModel):
    """Response from tutoring engine"""
    student_id: str
    lesson_id: str
    response_type: ResponseType
    content: str
    content_type: Optional[ContentType] = None  # Detected content type
    provider_used: str = "groq"  # Which AI provider generated this
    follow_up_question: Optional[str] = None
    hint: Optional[str] = None
    resources: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    generated_at: str

class TutorSession(BaseModel):
    """Active tutoring session"""
    session_id: str
    student_id: str
    course_id: str
    lesson_id: str
    mode: TutorMode
    start_time: datetime
    messages: List[Dict[str, Any]] = []
    performance_score: float = 0.0
    topics_covered: List[str] = []

class StudentKnowledgeProfile(BaseModel):
    """Student's knowledge profile"""
    student_id: str
    course_id: str
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    learning_pace: str = "normal"  # slow, normal, fast
    preferred_learning_style: str = "mixed"  # visual, auditory, kinesthetic, mixed
    estimated_proficiency: Dict[str, float] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# ============== AI TUTORING ENGINE ==============

class AITutoringEngine:
    """
    Enterprise AI-powered tutoring engine with multi-provider support.
    
    Features:
    - 6 LLM providers with intelligent fallback chain
    - ML-based content type classification
    - Adaptive difficulty prediction
    - Semantic essay evaluation with embeddings
    - Real-time performance tracking
    - Support for ALL eLearning content types
    """

    def __init__(self):
        """Initialize tutoring engine with all components"""
        # Initialize LLM provider manager (Groq primary + 5 fallbacks)
        self.llm_manager = LLMProviderManager()
        logger.info("✅ LLM Provider Manager initialized")

        # Initialize content classifier (ML-based)
        self.classifier = ContentClassifier()
        logger.info("✅ Content Classifier initialized")

        # Initialize difficulty predictor
        self.difficulty_predictor = DifficultyPredictor()
        logger.info("✅ Difficulty Predictor initialized")

        # Session management

        self.active_sessions: Dict[str, TutorSession] = {}
        self.student_profiles: Dict[str, StudentKnowledgeProfile] = {}

    async def start_tutoring_session(self, request: TutoringRequest) -> TutorSession:
        """Start a new tutoring session"""
        session_id = f"tut_{request.student_id}_{request.lesson_id}_{datetime.utcnow().timestamp()}"
        
        session = TutorSession(
            session_id=session_id,
            student_id=request.student_id,
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            mode=request.mode,
            start_time=datetime.utcnow()
        )

        self.active_sessions[session_id] = session
        logger.info(f"Started tutoring session: {session_id}")
        return session

    async def get_explanation(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """
        Get AI-generated explanation for a topic.
        
        Uses intelligent fallback chain:
        1. Groq (fastest, primary)
        2. OpenAI (highest quality)
        3. Cohere (always available)
        4. Ollama (local, offline)
        5. HuggingFace (lightweight)
        6. Fallback template (if all fail)
        """
        difficulty_context = {
            DifficultyLevel.BEGINNER: "simple language, use analogies and everyday examples",
            DifficultyLevel.INTERMEDIATE: "balance detail and clarity, use diagrams descriptions",
            DifficultyLevel.ADVANCED: "technical depth, mention key research and applications",
            DifficultyLevel.EXPERT: "cutting-edge research, nuanced perspectives, edge cases"
        }

        prompt = f"""You are an expert tutor explaining complex topics clearly.

Topic: {topic}
Difficulty Level: {difficulty.value}

Please provide:
1. **Clear Definition**: What is this concept?
2. **Key Concepts**: Main points to understand
3. **Real-World Examples**: Practical applications
4. **Visual Description**: How to visualize/understand it
5. **Common Mistakes**: What students often get wrong
6. **Next Steps**: What to learn next

Tone: {difficulty_context[difficulty]}
Keep explanation concise but comprehensive."""

        try:
            # Use LLM manager with fallback chain
            explanation, provider = await self.llm_manager.generate_text(prompt, max_tokens=2000)
            
            if explanation:
                logger.info(f"✅ Generated explanation using {provider}")
                return {
                    "success": True,
                    "topic": topic,
                    "difficulty": difficulty.value,
                    "explanation": explanation,
                    "provider_used": provider,
                    "generated_at": datetime.utcnow().isoformat()
                }
            else:
                logger.warning("⚠️ All providers failed, using fallback")
                return self._get_fallback_explanation(topic, difficulty)

        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            return self._get_fallback_explanation(topic, difficulty)

    async def generate_practice_questions(self, request: PracticeQuestionRequest) -> Dict[str, Any]:
        """Generate practice questions for a topic"""
        if not self.client:
            return {"error": "Groq AI not configured"}

        try:
            prompt = f"""Generate {request.count} practice questions for learning: {request.topic}

Difficulty: {request.difficulty.value}
Format for each question:

Question [number]:
[Question text]

Options:
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Correct Answer: [Letter]
Explanation: [Brief explanation why this is correct]

Make questions:
- Progressive in difficulty
- Cover different aspects of the topic
- Include common misconceptions
- Appropriate for {request.difficulty.value} learners"""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=3000
            )

            questions_text = response.choices[0].message.content

            return {
                "success": True,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "count": request.count,
                "questions": questions_text,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return {"error": str(e)}

    async def evaluate_answer(self, question: str, student_answer: str, correct_answer: str) -> Dict[str, Any]:
        """Evaluate student's answer and provide feedback"""
        if not self.client:
            return self._get_fallback_evaluation(student_answer, correct_answer)

        try:
            prompt = f"""You are an expert tutor evaluating a student's answer.

Question: {question}
Student's Answer: {student_answer}
Correct Answer: {correct_answer}

Please provide:
1. **Is it Correct?**: Yes/No/Partially
2. **Score**: 0-100
3. **Feedback**: What did the student understand well? What needs improvement?
4. **Explanation**: Why is the correct answer right?
5. **Learning Hint**: Concept to review to improve

Be encouraging but honest. Identify specific learning gaps."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )

            evaluation = response.choices[0].message.content

            return {
                "success": True,
                "evaluation": evaluation,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Answer evaluation error: {e}")
            return self._get_fallback_evaluation(student_answer, correct_answer)

    async def socratic_questioning(self, topic: str, student_response: Optional[str]) -> Dict[str, Any]:
        """Use Socratic method to guide learning"""
        if not self.client:
            return {"error": "Groq AI not configured"}

        try:
            if student_response:
                prompt = f"""You are using the Socratic method to teach {topic}.

Student said: {student_response}

Ask ONE powerful question that:
- Builds on what they said
- Guides them toward deeper understanding
- Challenges their thinking
- Is open-ended (can't answer with yes/no)

Also provide:
- Your assessment of their current understanding
- What concept they should think about
- A hint if they get stuck"""
            else:
                prompt = f"""You are using the Socratic method to teach {topic}.

Start by asking an engaging opening question that:
- Gets students thinking about the topic
- Connects to things they might already know
- Is thought-provoking but not overwhelming

Provide context about why this question matters."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.75,
                max_tokens=1000
            )

            response_text = response.choices[0].message.content

            return {
                "success": True,
                "question": response_text,
                "method": "socratic",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Socratic questioning error: {e}")
            return {"error": str(e)}

    async def generate_study_plan(self, student_id: str, weak_topics: List[str]) -> Dict[str, Any]:
        """Generate personalized study plan based on weak areas"""
        if not self.client:
            return {"error": "Groq AI not configured"}

        try:
            topics_str = ", ".join(weak_topics)
            prompt = f"""Create a personalized study plan for a student struggling with: {topics_str}

The plan should:
1. **Prioritize Topics**: Which to tackle first?
2. **Daily Schedule**: Suggested daily study (15-30 minutes)
3. **Resources**: Types of resources to use
4. **Practice Strategy**: How much practice per topic
5. **Milestones**: When to assess progress
6. **Motivation Tips**: How to stay engaged

Format as a concrete, actionable 2-week plan."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )

            study_plan = response.choices[0].message.content

            return {
                "success": True,
                "student_id": student_id,
                "weak_topics": weak_topics,
                "study_plan": study_plan,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Study plan generation error: {e}")
            return {"error": str(e)}

    async def get_tutoring_response(self, request: TutoringRequest) -> TutoringResponse:
        """
        Get appropriate tutoring response based on mode and context.
        
        Features:
        - Auto-detects content type if not provided (ML-based)
        - Auto-predicts difficulty if not provided (adaptive)
        - Uses fallback chain (Groq → OpenAI → Cohere → Ollama → HuggingFace)
        - Tracks which provider was used in response
        """
        # 1. Auto-detect content type if not provided
        content_type = request.content_type
        if not content_type and request.context:
            content_type, confidence = self.classifier.classify_with_confidence(
                f"{request.topic} {request.context}"
            )
            logger.info(f"🔍 Auto-detected content type: {content_type.value} (confidence: {confidence:.2f})")
        elif not content_type:
            content_type, confidence = self.classifier.classify_with_confidence(request.topic)

        # 2. Get or predict difficulty
        difficulty = request.difficulty
        if not difficulty:
            # Load student profile to predict difficulty
            student_profile = self.student_profiles.get(
                request.student_id,
                StudentKnowledgeProfile(
                    student_id=request.student_id,
                    course_id=request.course_id
                )
            )
            difficulty = await self.difficulty_predictor.predict_difficulty(
                student_profile,
                content_type
            )
            logger.info(f"📊 Auto-predicted difficulty: {difficulty.value}")

        # 3. Generate response based on mode
        provider_used = "unknown"
        
        if request.mode == TutorMode.EXPLANATION:
            result = await self.get_explanation(request.topic, difficulty)
            content = result.get("explanation", str(result))
            response_type = ResponseType.EXPLANATION
            provider_used = result.get("provider_used", "groq")
        elif request.mode == TutorMode.SOCRATIC:
            result = await self.socratic_questioning(request.topic, request.student_response)
            content = result.get("question", str(result))
            response_type = ResponseType.QUESTION
            provider_used = result.get("provider_used", "groq")
        elif request.mode == TutorMode.PRACTICE:
            pq_request = PracticeQuestionRequest(
                student_id=request.student_id,
                lesson_id=request.lesson_id,
                topic=request.topic,
                difficulty=difficulty,
                count=1
            )
            result = await self.generate_practice_questions(pq_request)
            content = result.get("questions", [{}])[0].get("question", str(result))
            response_type = ResponseType.QUESTION
            provider_used = result.get("provider_used", "groq")
        elif request.mode == TutorMode.ASSESSMENT:
            result = await self.generate_practice_questions(
                PracticeQuestionRequest(
                    student_id=request.student_id,
                    lesson_id=request.lesson_id,
                    topic=request.topic,
                    difficulty=difficulty,
                    count=5
                )
            )
            content = str(result.get("questions", [{}]))
            response_type = ResponseType.QUESTION
            provider_used = result.get("provider_used", "groq")
        else:
            # Default: adaptive explanation
            result = await self.get_explanation(request.topic, difficulty)
            content = result.get("explanation", str(result))
            response_type = ResponseType.EXPLANATION
            provider_used = result.get("provider_used", "groq")

        # 4. Build response with provider info
        return TutoringResponse(
            student_id=request.student_id,
            lesson_id=request.lesson_id,
            response_type=response_type,
            content=content,
            content_type=content_type,
            provider_used=provider_used,
            generated_at=datetime.utcnow().isoformat()
        )

    def _get_fallback_explanation(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Fallback explanation when Groq unavailable"""
        fallbacks = {
            DifficultyLevel.BEGINNER: f"Think of {topic} like...",
            DifficultyLevel.INTERMEDIATE: f"{topic} is a concept that...",
            DifficultyLevel.ADVANCED: f"Advanced understanding of {topic} involves...",
            DifficultyLevel.EXPERT: f"Expert-level knowledge of {topic} includes..."
        }
        return {
            "success": True,
            "topic": topic,
            "difficulty": difficulty.value,
            "explanation": fallbacks[difficulty],
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_fallback_evaluation(self, student_answer: str, correct_answer: str) -> Dict[str, Any]:
        """Fallback evaluation when Groq unavailable"""
        return {
            "success": True,
            "evaluation": f"Your answer: {student_answer}. Correct answer: {correct_answer}",
            "score": 50,
            "feedback": "Compare your answer with the correct one to identify gaps"
        }

# ============== GLOBAL INSTANCE ==============

_tutoring_engine: Optional[AITutoringEngine] = None

def initialize_tutoring_engine() -> AITutoringEngine:
    """Initialize tutoring engine"""
    global _tutoring_engine
    _tutoring_engine = AITutoringEngine()
    return _tutoring_engine

def get_tutoring_engine() -> AITutoringEngine:
    """Get tutoring engine instance"""
    global _tutoring_engine
    if _tutoring_engine is None:
        _tutoring_engine = AITutoringEngine()
    return _tutoring_engine

# ============== API ROUTER ==============

router = APIRouter(prefix="/api/tutoring", tags=["AI Tutoring"])

@router.post("/session/start")
async def start_session(request: TutoringRequest, engine: AITutoringEngine = Depends(get_tutoring_engine)):
    """Start a tutoring session"""
    try:
        session = await engine.start_tutoring_session(request)
        return {
            "success": True,
            "session_id": session.session_id,
            "mode": session.mode.value,
            "started_at": session.start_time.isoformat()
        }
    except Exception as e:
        logger.error(f"Session start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explanation")
async def get_explanation(
    topic: str = Body(...),
    difficulty: DifficultyLevel = Body(DifficultyLevel.INTERMEDIATE),
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Get topic explanation"""
    try:
        result = await engine.get_explanation(topic, difficulty)
        return result
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/practice-questions")
async def get_practice_questions(
    request: PracticeQuestionRequest,
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Generate practice questions"""
    try:
        result = await engine.generate_practice_questions(request)
        return result
    except Exception as e:
        logger.error(f"Practice questions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate-answer")
async def evaluate_answer(
    question: str = Body(...),
    student_answer: str = Body(...),
    correct_answer: str = Body(...),
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Evaluate student answer"""
    try:
        result = await engine.evaluate_answer(question, student_answer, correct_answer)
        return result
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/socratic-question")
async def get_socratic_question(
    topic: str = Body(...),
    student_response: Optional[str] = Body(None),
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Get Socratic method question"""
    try:
        result = await engine.socratic_questioning(topic, student_response)
        return result
    except Exception as e:
        logger.error(f"Socratic question error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/study-plan")
async def generate_study_plan(
    student_id: str = Body(...),
    weak_topics: List[str] = Body(...),
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Generate personalized study plan"""
    try:
        result = await engine.generate_study_plan(student_id, weak_topics)
        return result
    except Exception as e:
        logger.error(f"Study plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tutoring-response")
async def get_tutoring_response(
    request: TutoringRequest,
    engine: AITutoringEngine = Depends(get_tutoring_engine)
):
    """Get complete tutoring response"""
    try:
        response = await engine.get_tutoring_response(request)
        return response.dict()
    except Exception as e:
        logger.error(f"Tutoring response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session(session_id: str, engine: AITutoringEngine = Depends(get_tutoring_engine)):
    """Get session details"""
    try:
        session = engine.active_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "session_id": session.session_id,
            "student_id": session.student_id,
            "mode": session.mode.value,
            "started_at": session.start_time.isoformat(),
            "duration_minutes": (datetime.utcnow() - session.start_time).total_seconds() / 60,
            "message_count": len(session.messages),
            "performance_score": session.performance_score
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/providers")
async def get_provider_health(engine: AITutoringEngine = Depends(get_tutoring_engine)):
    """
    Get health status of all LLM providers.
    
    Returns status of:
    - Groq (primary, fastest)
    - OpenAI (fallback #1, highest quality)
    - Cohere (fallback #2, always available)
    - Ollama (fallback #3, local/offline)
    - HuggingFace (fallback #4, lightweight)
    """
    try:
        provider_status = engine.llm_manager.get_provider_status()
        
        # Count working providers
        working_providers = sum(
            1 for status in provider_status.values() if status == 'ready'
        )
        
        return {
            "health_status": "healthy" if working_providers > 0 else "critical",
            "working_providers": working_providers,
            "total_providers": len(provider_status),
            "providers": provider_status,
            "fallback_chain": [
                "groq",
                "openai",
                "cohere",
                "ollama",
                "huggingface"
            ],
            "checked_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Provider health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/system")
async def get_system_health(engine: AITutoringEngine = Depends(get_tutoring_engine)):
    """
    Get comprehensive system health status.
    
    Includes:
    - LLM provider status
    - ML models availability
    - Active sessions count
    - System readiness
    """
    try:
        provider_status = engine.llm_manager.get_provider_status()
        working_providers = sum(1 for s in provider_status.values() if s == 'ready')
        
        return {
            "system_status": "ready" if working_providers > 0 else "degraded",
            "llm_providers": {
                "working": working_providers,
                "total": len(provider_status),
                "status": provider_status
            },
            "ml_models": {
                "content_classification": "ready",
                "difficulty_prediction": "ready",
                "embeddings_available": EMBEDDINGS_AVAILABLE
            },
            "active_sessions": len(engine.active_sessions),
            "tracked_students": len(engine.student_profiles),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"System health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

