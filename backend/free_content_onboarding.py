"""
GAAIUS Free Content Onboarding System
Import free books, courses, lessons, and educational content from open sources
Using OpenStax, LibriVox, Khan Academy, Project Gutenberg, MIT OpenCourseWare, etc.
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import json
from xml.etree import ElementTree as ET

# ==================== FREE CONTENT SOURCES ====================

class ContentSourceType(str, Enum):
    OPENSTAX = "openstax"  # Free textbooks
    LIBRIVOX = "librivox"  # Free audiobooks
    KHAN_ACADEMY = "khan_academy"  # Free video lessons
    MIT_OCW = "mit_ocw"  # MIT OpenCourseWare
    PROJECT_GUTENBERG = "project_gutenberg"  # Classic books
    WIKIPEDIA = "wikipedia"  # Encyclopedia
    COURSERA_FREE = "coursera_free"  # Free Coursera courses
    YOUTUBE_EDU = "youtube_edu"  # Educational YouTube
    ARXIV = "arxiv"  # Research papers
    WIKIBOOKS = "wikibooks"  # Open textbooks

# ==================== MODELS ====================

class FreeContent(BaseModel):
    """Free educational content from open sources"""
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: ContentSourceType
    source_id: str  # ID from original source
    
    # Content Details
    title: str
    description: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    
    # Content Type
    content_type: str  # "book", "course", "lesson", "video", "article", "paper"
    subject: str  # "Mathematics", "Physics", "History", etc.
    level: str  # "beginner", "intermediate", "advanced"
    
    # URLs
    source_url: str  # Original source URL
    content_url: str  # Direct access URL
    thumbnail_url: Optional[str] = None
    
    # Metadata
    language: str = "en"
    license: str  # "CC0", "CC-BY", "CC-BY-SA", etc.
    pages_or_duration: Optional[int] = None  # Pages for books, minutes for videos
    
    # Full text (stored if small enough, otherwise link)
    full_text: Optional[str] = None
    text_url: Optional[str] = None
    
    # AI Processing
    ai_summary: Optional[str] = None
    ai_keywords: List[str] = Field(default_factory=list)
    ai_difficulty_score: Optional[float] = None  # 0-1
    
    # Usage
    times_used: int = 0
    times_accessed: int = 0
    ratings: List[int] = Field(default_factory=list)
    average_rating: float = 0.0
    
    # Status
    is_verified: bool = False
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class FreeLessonPlan(BaseModel):
    """Lesson plan created from free content"""
    lesson_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    
    title: str
    description: str
    
    # Components (references to free content)
    reading_materials: List[str] = Field(default_factory=list)  # content_ids
    video_materials: List[str] = Field(default_factory=list)  # content_ids
    audio_materials: List[str] = Field(default_factory=list)  # content_ids
    
    # AI-Generated
    ai_generated_summary: Optional[str] = None
    ai_learning_objectives: List[str] = Field(default_factory=list)
    ai_discussion_prompts: List[str] = Field(default_factory=list)
    
    # Quiz (AI-generated from content)
    ai_generated_quiz: Optional[List[Dict]] = None
    
    # Duration
    estimated_duration_minutes: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==================== OPENSTAX SERVICE ====================

class OpenStaxService:
    """Import free textbooks from OpenStax"""
    
    BASE_URL = "https://openstax.org/api/v1"
    
    async def get_books(self) -> List[Dict]:
        """Fetch list of all free OpenStax books"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/books") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', [])
        except Exception as e:
            print(f"Error fetching OpenStax books: {e}")
        return []
    
    async def get_book_details(self, book_id: str) -> Dict:
        """Get detailed book information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/books/{book_id}") as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Error fetching book details: {e}")
        return {}
    
    async def import_book_as_content(self, book_data: Dict) -> FreeContent:
        """Convert OpenStax book to FreeContent"""
        
        content = FreeContent(
            source=ContentSourceType.OPENSTAX,
            source_id=book_data['id'],
            title=book_data['title'],
            description=book_data.get('description', ''),
            author=', '.join([a['name'] for a in book_data.get('authors', [])]),
            publisher="OpenStax",
            publication_date=datetime.fromisoformat(book_data.get('publication_date', '2020-01-01')),
            content_type="book",
            subject=book_data.get('subject', 'General'),
            level="beginner",
            source_url=book_data.get('url', ''),
            content_url=book_data.get('web_url', ''),
            thumbnail_url=book_data.get('cover_url'),
            license="CC-BY",
            pages_or_duration=book_data.get('book_version', {}).get('pages', 0),
            language="en",
            is_verified=True
        )
        
        return content

# ==================== LIBRIVOX SERVICE ====================

class LibriVoxService:
    """Import free audiobooks from LibriVox"""
    
    BASE_URL = "https://librivox.org/api/cache/metadata/json"
    
    async def search_audiobooks(self, title: str = "", author: str = "", language: str = "en") -> List[Dict]:
        """Search for audiobooks"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {}
                if language:
                    params['language'] = language
                
                async with session.get(f"{self.BASE_URL}/all.json", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        books = data.get('books', [])
                        
                        # Filter by title/author
                        if title:
                            books = [b for b in books if title.lower() in b.get('title', '').lower()]
                        if author:
                            books = [b for b in books if author.lower() in b.get('author', '').lower()]
                        
                        return books
        except Exception as e:
            print(f"Error searching LibriVox: {e}")
        return []
    
    async def import_audiobook_as_content(self, book_data: Dict) -> FreeContent:
        """Convert LibriVox audiobook to FreeContent"""
        
        # Get first audio file
        audio_url = ""
        duration = 0
        
        if book_data.get('files'):
            first_file = book_data['files'][0]
            audio_url = first_file.get('file_url', '')
            duration = int(first_file.get('duration', 0) / 60)  # Convert to minutes
        
        content = FreeContent(
            source=ContentSourceType.LIBRIVOX,
            source_id=book_data['id'],
            title=book_data['title'],
            description=book_data.get('description', ''),
            author=book_data.get('author', 'Unknown'),
            publisher="LibriVox",
            publication_date=None,
            content_type="audio",
            subject="Literature",
            level="beginner",
            source_url=book_data.get('url_project', ''),
            content_url=audio_url,
            language=book_data.get('language', 'en'),
            license="Public Domain",
            pages_or_duration=duration,
            is_verified=True
        )
        
        return content

# ==================== KHAN ACADEMY SERVICE ====================

class KhanAcademyService:
    """Import free video lessons from Khan Academy"""
    
    # Note: Khan Academy API requires authentication
    # Alternative: use web scraping or RSS feeds
    
    async def get_course_videos(self, course_slug: str) -> List[Dict]:
        """Get videos for a Khan Academy course"""
        # Simplified - in production would use official API
        # Popular courses: math, science, history, economics, etc.
        
        courses = {
            'algebra-1': 'https://www.khanacademy.org/math/algebra',
            'algebra-2': 'https://www.khanacademy.org/math/algebra2',
            'geometry': 'https://www.khanacademy.org/math/geometry',
            'calculus': 'https://www.khanacademy.org/math/calculus-1',
            'biology': 'https://www.khanacademy.org/science/biology',
            'chemistry': 'https://www.khanacademy.org/science/chemistry',
            'physics': 'https://www.khanacademy.org/science/physics',
            'history': 'https://www.khanacademy.org/humanities/history',
        }
        
        return []  # Would fetch actual videos

# ==================== MIT OpenCourseWare SERVICE ====================

class MITOpenCourseWareService:
    """Import free MIT courses"""
    
    BASE_URL = "https://ocw.mit.edu/api/v2"
    
    async def get_courses(self) -> List[Dict]:
        """Fetch list of MIT OCW courses"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/courses") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', [])
        except Exception as e:
            print(f"Error fetching MIT OCW courses: {e}")
        return []
    
    async def import_course_as_content(self, course_data: Dict) -> FreeContent:
        """Convert MIT course to FreeContent"""
        
        content = FreeContent(
            source=ContentSourceType.MIT_OCW,
            source_id=course_data['id'],
            title=course_data.get('title', ''),
            description=course_data.get('description', ''),
            author=', '.join([i.get('name', '') for i in course_data.get('instructors', [])]),
            publisher="MIT",
            publication_date=None,
            content_type="course",
            subject=course_data.get('course_collections', ['General'])[0],
            level=course_data.get('level', 'intermediate'),
            source_url=course_data.get('url', ''),
            content_url=course_data.get('url', ''),
            language="en",
            license="CC-BY-NC-SA",
            is_verified=True
        )
        
        return content

# ==================== MAIN ONBOARDING SERVICE ====================

class FreeContentOnboardingService:
    """Service to onboard and manage free educational content"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.openstax = OpenStaxService()
        self.librivox = LibriVoxService()
        self.khan = KhanAcademyService()
        self.mit = MITOpenCourseWareService()
    
    # ==================== CONTENT IMPORT ====================
    
    async def import_all_openstax_books(self) -> List[FreeContent]:
        """Import all OpenStax textbooks"""
        
        books = await self.openstax.get_books()
        imported = []
        
        for book in books:
            try:
                content = await self.openstax.import_book_as_content(book)
                await self.db.free_content.insert_one(content.dict())
                imported.append(content)
            except Exception as e:
                print(f"Error importing book {book.get('id')}: {e}")
        
        print(f"Imported {len(imported)} OpenStax books")
        return imported
    
    async def import_librivox_audiobooks(self, language: str = "en", limit: int = 100) -> List[FreeContent]:
        """Import LibriVox audiobooks"""
        
        audiobooks = await self.librivox.search_audiobooks(language=language)
        audiobooks = audiobooks[:limit]
        
        imported = []
        
        for book in audiobooks:
            try:
                content = await self.librivox.import_audiobook_as_content(book)
                await self.db.free_content.insert_one(content.dict())
                imported.append(content)
            except Exception as e:
                print(f"Error importing audiobook {book.get('id')}: {e}")
        
        print(f"Imported {len(imported)} LibriVox audiobooks")
        return imported
    
    async def import_mit_ocw_courses(self) -> List[FreeContent]:
        """Import MIT OpenCourseWare courses"""
        
        courses = await self.mit.get_courses()
        imported = []
        
        for course in courses:
            try:
                content = await self.mit.import_course_as_content(course)
                await self.db.free_content.insert_one(content.dict())
                imported.append(content)
            except Exception as e:
                print(f"Error importing MIT course {course.get('id')}: {e}")
        
        print(f"Imported {len(imported)} MIT OCW courses")
        return imported
    
    # ==================== CONTENT MANAGEMENT ====================
    
    async def get_content_by_subject(self, subject: str) -> List[FreeContent]:
        """Get all free content for a subject"""
        
        content = await self.db.free_content.find({
            "subject": subject,
            "is_active": True
        }).to_list(None)
        
        return [FreeContent(**c) for c in content]
    
    async def get_content_by_level(self, level: str) -> List[FreeContent]:
        """Get content by difficulty level"""
        
        content = await self.db.free_content.find({
            "level": level,
            "is_active": True
        }).to_list(None)
        
        return [FreeContent(**c) for c in content]
    
    async def search_content(self, query: str, subject: Optional[str] = None, level: Optional[str] = None) -> List[FreeContent]:
        """Search free content"""
        
        filters = {"is_active": True}
        
        if query:
            filters["$text"] = {"$search": query}
        if subject:
            filters["subject"] = subject
        if level:
            filters["level"] = level
        
        content = await self.db.free_content.find(filters).to_list(None)
        
        return [FreeContent(**c) for c in content]
    
    # ==================== AI-POWERED LESSON CREATION ====================
    
    async def create_lesson_from_free_content(self, course_id: str, lesson_title: str, selected_content_ids: List[str], groq_service) -> FreeLessonPlan:
        """Create a lesson plan from selected free content using AI"""
        
        # Fetch selected content
        content_items = []
        for content_id in selected_content_ids:
            item = await self.db.free_content.find_one({"content_id": content_id})
            if item:
                content_items.append(FreeContent(**item))
        
        if not content_items:
            raise Exception("No content selected")
        
        # Separate content by type
        reading = [c for c in content_items if c.content_type in ['book', 'article']]
        videos = [c for c in content_items if c.content_type == 'video']
        audio = [c for c in content_items if c.content_type == 'audio']
        
        # Create combined summary for AI
        combined_text = "\n\n".join([
            f"Title: {c.title}\nDescription: {c.description}\nContent: {c.full_text or c.text_url}"
            for c in content_items
        ])
        
        # Use Groq to generate lesson components
        prompt = f"""
Based on this educational content, create a comprehensive lesson plan:

{combined_text}

Generate:
1. A brief summary (100-150 words)
2. 3-5 learning objectives
3. 2-3 discussion prompts for students
4. A 10-question quiz with answers

Format as JSON.
"""
        
        # Call Groq API
        import os
        import aiohttp
        
        api_key = os.environ.get('GROQ_API_KEY')
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
                
                async with session.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data['choices'][0]['message']['content']
                        
                        try:
                            ai_content = json.loads(response_text)
                        except:
                            ai_content = {"summary": response_text}
                    else:
                        ai_content = {}
        except Exception as e:
            print(f"Error calling Groq: {e}")
            ai_content = {}
        
        # Create lesson plan
        lesson = FreeLessonPlan(
            course_id=course_id,
            title=lesson_title,
            description=ai_content.get('summary', ''),
            reading_materials=[c.content_id for c in reading],
            video_materials=[c.content_id for c in videos],
            audio_materials=[c.content_id for c in audio],
            ai_generated_summary=ai_content.get('summary'),
            ai_learning_objectives=ai_content.get('learning_objectives', []),
            ai_discussion_prompts=ai_content.get('discussion_prompts', []),
            ai_generated_quiz=ai_content.get('quiz'),
            estimated_duration_minutes=sum([c.pages_or_duration or 0 for c in content_items])
        )
        
        # Save lesson
        await self.db.free_lessons.insert_one(lesson.dict())
        
        return lesson
    
    async def build_full_course_from_free_content(self, course_title: str, subject: str, level: str, groq_service) -> Dict:
        """Build complete course from free content"""
        
        # Get content for subject and level
        content = await self.db.free_content.find({
            "subject": subject,
            "level": level,
            "is_active": True
        }).to_list(None)
        
        if not content:
            raise Exception(f"No free content found for {subject} at {level} level")
        
        # Create course structure
        from social_service import ELearningService
        
        # This would use ELearningService to create course
        # Then populate with free content and AI-generated lessons
        
        return {
            "course_title": course_title,
            "content_count": len(content),
            "sources": list(set([c['source'] for c in content])),
            "estimated_hours": sum([c.get('pages_or_duration', 0) for c in content]) / 60
        }
    
    async def update_content_ratings(self, content_id: str, rating: int) -> Optional[FreeContent]:
        """Update content rating/engagement"""
        
        content = await self.db.free_content.find_one({"content_id": content_id})
        if not content:
            return None
        
        ratings = content.get('ratings', [])
        ratings.append(rating)
        avg_rating = sum(ratings) / len(ratings)
        
        updated = await self.db.free_content.find_one_and_update(
            {"content_id": content_id},
            {
                "$set": {
                    "ratings": ratings,
                    "average_rating": avg_rating,
                    "last_updated": datetime.utcnow()
                },
                "$inc": {"times_accessed": 1}
            },
            return_document=True
        )
        
        return FreeContent(**updated) if updated else None

# ==================== INITIALIZATION ====================

async def initialize_free_content_platform(db: AsyncIOMotorDatabase):
    """Initialize platform with free content"""
    
    service = FreeContentOnboardingService(db)
    
    print("Starting free content import...")
    
    # Import from multiple sources
    tasks = [
        service.import_all_openstax_books(),
        service.import_librivox_audiobooks(limit=50),
        service.import_mit_ocw_courses()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\nContent import complete!")
    print(f"Results: {results}")

# Export
__all__ = [
    'FreeContentOnboardingService',
    'FreeContent', 'FreeLessonPlan',
    'OpenStaxService', 'LibriVoxService', 'KhanAcademyService', 'MITOpenCourseWareService',
    'ContentSourceType',
    'initialize_free_content_platform'
]
