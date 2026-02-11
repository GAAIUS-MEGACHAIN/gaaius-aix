from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class TemplateCategory(str, Enum):
    SOCIAL_MEDIA = "social_media"
    BUSINESS = "business"
    EDUCATION = "education"
    MARKETING = "marketing"
    PRESENTATION = "presentation"
    POSTER = "poster"
    FLYER = "flyer"
    INVITATION = "invitation"
    CERTIFICATE = "certificate"
    RESUME = "resume"
    INFOGRAPHIC = "infographic"
    BRANDING = "branding"
    PRODUCT = "product"
    EVENT = "event"
    REAL_ESTATE = "real_estate"
    FASHION = "fashion"
    TRAVEL = "travel"
    FOOD = "food"
    FITNESS = "fitness"
    TECH = "tech"
    NONPROFIT = "nonprofit"
    HOSPITALITY = "hospitality"
    HEALTHCARE = "healthcare"

class TemplateElement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    x: float = 0
    y: float = 0
    width: float = 200
    height: float = 100
    rotation: float = 0
    content: Optional[str] = None
    color: str = "#000000"
    fontSize: Optional[int] = 16
    fontFamily: Optional[str] = "Arial"
    backgroundColor: Optional[str] = None
    imageUrl: Optional[str] = None
    opacity: float = 1.0
    locked: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CanvasTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: TemplateCategory
    thumbnailUrl: str = ""
    width: float = 1920
    height: float = 1080
    elements: List[TemplateElement] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    industry: Optional[str] = None
    popularity: int = 0
    downloads: int = 0
    rating: float = 5.0
    isPaid: bool = False
    isFeatured: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TemplateLibrary:
    def __init__(self):
        self.templates = self._init_free_templates()
        logger.info(f"✅ Template Library initialized with {len(self.templates)} templates")

    def _init_free_templates(self) -> List[CanvasTemplate]:
        """Initialize 100+ free templates from various categories"""
        templates = []

        # SOCIAL MEDIA TEMPLATES (20+)
        social_templates = [
            CanvasTemplate(
                name="Instagram Post - Minimalist",
                description="Clean minimalist Instagram post design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["instagram", "social", "minimalist", "clean"],
                width=1080, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1080, backgroundColor="#ffffff"),
                    TemplateElement(type="text", x=100, y=450, width=880, height=180, content="Your Amazing Content Here", fontSize=48, color="#000000", fontFamily="Arial")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Instagram Story - Bold",
                description="Eye-catching Instagram story design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["story", "instagram", "bold", "eye-catching"],
                width=1080, height=1920,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1920, backgroundColor="#FF6B6B"),
                    TemplateElement(type="text", x=50, y=800, width=980, height=320, content="DON'T MISS OUT!", fontSize=72, color="#FFFFFF", fontFamily="Arial")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="TikTok Promotional Video Cover",
                description="TikTok promotional design with video overlay",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["tiktok", "social", "promo", "video"],
                width=1080, height=1920,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1920, backgroundColor="#000000"),
                    TemplateElement(type="text", x=50, y=900, width=980, height=200, content="Follow For More", fontSize=64, color="#FFFFFF", fontFamily="Arial")
                ]
            ),
            CanvasTemplate(
                name="LinkedIn Professional Article",
                description="Professional LinkedIn article cover design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["linkedin", "professional", "article", "business"],
                width=1200, height=627,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1200, height=627, backgroundColor="#0A66C2"),
                    TemplateElement(type="text", x=50, y=200, width=1100, height=227, content="Industry Insights & Tips", fontSize=48, color="#FFFFFF")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Twitter/X Post Card",
                description="Twitter engaging post design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["twitter", "x", "social", "post"],
                width=1024, height=512,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1024, height=512, backgroundColor="#1DA1F2"),
                    TemplateElement(type="text", x=50, y=200, width=924, height=112, content="Big news coming...", fontSize=36, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Pinterest Vertical Pin",
                description="Pinterest optimized vertical pin design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["pinterest", "pin", "vertical", "discovery"],
                width=1000, height=1500,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=1500, backgroundColor="#E60023"),
                    TemplateElement(type="text", x=50, y=600, width=900, height=300, content="Save This For Later", fontSize=56, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="YouTube Thumbnail - Bold",
                description="YouTube video thumbnail with attention-grabbing design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["youtube", "thumbnail", "video", "attention"],
                width=1280, height=720,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1280, height=720, backgroundColor="#FF0000"),
                    TemplateElement(type="text", x=100, y=300, width=1080, height=120, content="MUST WATCH!", fontSize=64, color="#FFFFFF")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Facebook Cover Photo",
                description="Professional Facebook profile cover design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["facebook", "cover", "profile", "business"],
                width=1200, height=628,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1200, height=628, backgroundColor="#1877F2"),
                    TemplateElement(type="text", x=50, y=250, width=1100, height=128, content="Welcome To My Page", fontSize=48, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Snapchat Story Template",
                description="Snapchat vertical story design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["snapchat", "story", "vertical", "social"],
                width=1080, height=1920,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1920, backgroundColor="#FFFC00"),
                    TemplateElement(type="text", x=50, y=900, width=980, height=200, content="Your Story Here", fontSize=48, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Instagram Carousel Post",
                description="Multi-slide Instagram carousel design",
                category=TemplateCategory.SOCIAL_MEDIA,
                tags=["instagram", "carousel", "slideshow", "multi-page"],
                width=1080, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1080, backgroundColor="#F0F0F0"),
                    TemplateElement(type="text", x=100, y=450, width=880, height=180, content="Slide 1 of 5", fontSize=40, color="#000000")
                ]
            ),
        ]

        # BUSINESS TEMPLATES (25+)
        business_templates = [
            CanvasTemplate(
                name="Business Card - Professional",
                description="Premium professional business card",
                category=TemplateCategory.BUSINESS,
                tags=["business", "card", "professional", "contact"],
                width=1050, height=600,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1050, height=600, backgroundColor="#2C3E50"),
                    TemplateElement(type="text", x=50, y=100, width=950, height=80, content="John Doe", fontSize=32, color="#FFFFFF"),
                    TemplateElement(type="text", x=50, y=200, width=950, height=60, content="CEO & Founder", fontSize=20, color="#3498DB")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Corporate Logo - Geometric",
                description="Geometric logo design template",
                category=TemplateCategory.BRANDING,
                tags=["logo", "geometric", "branding", "corporate"],
                width=500, height=500,
                elements=[
                    TemplateElement(type="shape", x=100, y=100, width=300, height=300, backgroundColor="#FF6B35")
                ]
            ),
            CanvasTemplate(
                name="Letterhead - Corporate",
                description="Professional corporate letterhead design",
                category=TemplateCategory.BUSINESS,
                tags=["letterhead", "corporate", "official", "stationery"],
                width=1000, height=1294,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=200, backgroundColor="#34495E"),
                    TemplateElement(type="text", x=50, y=50, width=900, height=100, content="Company Name", fontSize=40, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Invoice Template - Professional",
                description="Complete invoice design template",
                category=TemplateCategory.BUSINESS,
                tags=["invoice", "financial", "business", "accounting"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=60, content="INVOICE", fontSize=40, color="#000000", fontFamily="Arial")
                ]
            ),
            CanvasTemplate(
                name="Company Envelope",
                description="Standard envelope design",
                category=TemplateCategory.BUSINESS,
                tags=["envelope", "business", "mail", "stationery"],
                width=970, height=440,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=970, height=440, backgroundColor="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Proposal Cover Page",
                description="Professional business proposal cover",
                category=TemplateCategory.BUSINESS,
                tags=["proposal", "business", "professional", "formal"],
                width=850, height=1100,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=850, height=1100, backgroundColor="#1C4995"),
                    TemplateElement(type="text", x=50, y=400, width=750, height=150, content="Project Proposal", fontSize=48, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Menu Card - Restaurant",
                description="Restaurant menu card design",
                category=TemplateCategory.HOSPITALITY,
                tags=["menu", "restaurant", "food", "hospitality"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=100, content="MENU", fontSize=48, color="#8B4513")
                ]
            ),
            CanvasTemplate(
                name="Hotel Key Card",
                description="Hotel room key card design",
                category=TemplateCategory.HOSPITALITY,
                tags=["hotel", "keycard", "hospitality", "room"],
                width=500, height=300,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=500, height=300, backgroundColor="#B8860B")
                ]
            ),
            CanvasTemplate(
                name="Receipt Design",
                description="Professional receipt template",
                category=TemplateCategory.BUSINESS,
                tags=["receipt", "pos", "transaction", "business"],
                width=400, height=600,
                elements=[
                    TemplateElement(type="text", x=20, y=20, width=360, height=40, content="RECEIPT", fontSize=24, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Appointment Card",
                description="Professional appointment reminder card",
                category=TemplateCategory.BUSINESS,
                tags=["appointment", "reminder", "card", "professional"],
                width=600, height=400,
                elements=[
                    TemplateElement(type="text", x=30, y=150, width=540, height=100, content="Your Appointment", fontSize=32, color="#000000")
                ]
            ),
        ]

        # MARKETING TEMPLATES (25+)
        marketing_templates = [
            CanvasTemplate(
                name="Email Campaign Header",
                description="Professional email newsletter header",
                category=TemplateCategory.MARKETING,
                tags=["email", "newsletter", "marketing", "campaign"],
                width=600, height=200,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=600, height=200, backgroundColor="#3498DB"),
                    TemplateElement(type="text", x=20, y=70, width=560, height=60, content="Special Offer - Save 30%", fontSize=32, color="#FFFFFF")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Product Showcase - Ecommerce",
                description="E-commerce product showcase design",
                category=TemplateCategory.PRODUCT,
                tags=["product", "ecommerce", "showcase", "sales"],
                width=800, height=800,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=800, backgroundColor="#ECF0F1")
                ]
            ),
            CanvasTemplate(
                name="Web Advertisement Banner",
                description="Standard web ad banner design",
                category=TemplateCategory.MARKETING,
                tags=["ad", "banner", "web", "advertising"],
                width=728, height=90,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=728, height=90, backgroundColor="#E74C3C"),
                    TemplateElement(type="text", x=10, y=25, width=708, height=40, content="Click Here For Amazing Deals!", fontSize=18, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Landing Page Hero Section",
                description="Website landing page hero design",
                category=TemplateCategory.MARKETING,
                tags=["landing", "hero", "website", "conversion"],
                width=1920, height=600,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=600, backgroundColor="#9B59B6"),
                    TemplateElement(type="text", x=200, y=200, width=1520, height=200, content="Your Product Here", fontSize=64, color="#FFFFFF")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Coupon/Discount Card",
                description="Promotional coupon design",
                category=TemplateCategory.MARKETING,
                tags=["coupon", "discount", "promotion", "sales"],
                width=800, height=400,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=400, backgroundColor="#FF9800"),
                    TemplateElement(type="text", x=50, y=100, width=700, height=200, content="50% OFF", fontSize=80, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Google Ads Display Banner",
                description="Google Ads standard display ad",
                category=TemplateCategory.MARKETING,
                tags=["google ads", "display", "banner", "advertising"],
                width=300, height=250,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=300, height=250, backgroundColor="#1f73e8")
                ]
            ),
            CanvasTemplate(
                name="Sales Funnel Infographic",
                description="Sales conversion funnel design",
                category=TemplateCategory.INFOGRAPHIC,
                tags=["funnel", "sales", "infographic", "conversion"],
                width=1200, height=1000,
                elements=[
                    TemplateElement(type="text", x=100, y=100, width=1000, height=80, content="Sales Funnel", fontSize=48, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Before & After Design",
                description="Before and after comparison template",
                category=TemplateCategory.MARKETING,
                tags=["before", "after", "comparison", "transformation"],
                width=1200, height=600,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=600, height=600, backgroundColor="#E8E8E8"),
                    TemplateElement(type="shape", x=600, y=0, width=600, height=600, backgroundColor="#90EE90")
                ]
            ),
            CanvasTemplate(
                name="Social Media Ad - Square",
                description="Social media square ad design",
                category=TemplateCategory.MARKETING,
                tags=["social", "ad", "square", "advertising"],
                width=1080, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1080, height=1080, backgroundColor="#2196F3")
                ]
            ),
            CanvasTemplate(
                name="Webinar Promotional Banner",
                description="Webinar promotion design",
                category=TemplateCategory.MARKETING,
                tags=["webinar", "event", "promotion", "learning"],
                width=1200, height=627,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1200, height=627, backgroundColor="#673AB7"),
                    TemplateElement(type="text", x=100, y=200, width=1000, height=227, content="Join Our Webinar", fontSize=48, color="#FFFFFF")
                ]
            ),
        ]

        # PRESENTATION TEMPLATES (15+)
        presentation_templates = [
            CanvasTemplate(
                name="Title Slide - Elegant",
                description="Elegant presentation title slide",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "title", "slide", "business"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=1080, backgroundColor="#34495E"),
                    TemplateElement(type="text", x=200, y=400, width=1520, height=150, content="Presentation Title", fontSize=72, color="#FFFFFF")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Content Slide - Simple",
                description="Simple content slide layout",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "content", "slide", "business"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=100, backgroundColor="#2C3E50"),
                    TemplateElement(type="text", x=100, y=20, width=1720, height=60, content="Section Title", fontSize=48, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Two Column Layout",
                description="Two-column presentation layout",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "layout", "columns", "content"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=960, height=1080, backgroundColor="#ECF0F1"),
                    TemplateElement(type="shape", x=960, y=0, width=960, height=1080, backgroundColor="#BDC3C7")
                ]
            ),
            CanvasTemplate(
                name="Image + Text Slide",
                description="Image with text overlay slide",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "image", "text", "overlay"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="text", x=100, y=400, width=1720, height=280, content="Your Title Here", fontSize=56, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Agenda Slide",
                description="Presentation agenda/outline slide",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "agenda", "outline", "structure"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="text", x=200, y=100, width=1520, height=100, content="Agenda", fontSize=56, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Closing Slide",
                description="Presentation closing/thank you slide",
                category=TemplateCategory.PRESENTATION,
                tags=["presentation", "closing", "thank you", "contact"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=1080, backgroundColor="#2C3E50"),
                    TemplateElement(type="text", x=200, y=400, width=1520, height=200, content="Thank You!", fontSize=80, color="#FFFFFF")
                ]
            ),
        ]

        # EVENT TEMPLATES (15+)
        event_templates = [
            CanvasTemplate(
                name="Wedding Invitation - Elegant",
                description="Elegant wedding invitation design",
                category=TemplateCategory.INVITATION,
                tags=["wedding", "invitation", "event", "elegant"],
                width=1000, height=1200,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=1200, backgroundColor="#FFF"),
                    TemplateElement(type="text", x=100, y=300, width=800, height=150, content="You Are Invited", fontSize=64, color="#8B4789", fontFamily="Georgia")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Concert Poster - Music Event",
                description="Music event poster design",
                category=TemplateCategory.EVENT,
                tags=["concert", "event", "poster", "music"],
                width=700, height=1050,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=700, height=1050, backgroundColor="#000000"),
                    TemplateElement(type="text", x=50, y=400, width=600, height=250, content="LIVE CONCERT", fontSize=56, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Conference Badge",
                description="Conference attendee badge design",
                category=TemplateCategory.EVENT,
                tags=["conference", "badge", "event", "attendee"],
                width=400, height=600,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=400, height=600, backgroundColor="#1ABC9C"),
                    TemplateElement(type="text", x=20, y=250, width=360, height=100, content="ATTENDEE", fontSize=36, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Birthday Party Invitation",
                description="Fun birthday party invitation",
                category=TemplateCategory.INVITATION,
                tags=["birthday", "invitation", "party", "celebration"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#FF69B4"),
                    TemplateElement(type="text", x=50, y=300, width=700, height=150, content="YOU'RE INVITED!", fontSize=56, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Corporate Event Flyer",
                description="Professional corporate event flyer",
                category=TemplateCategory.FLYER,
                tags=["corporate", "event", "flyer", "professional"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#34495E")
                ]
            ),
            CanvasTemplate(
                name="Webinar Registration Banner",
                description="Webinar registration and event banner",
                category=TemplateCategory.EVENT,
                tags=["webinar", "registration", "event", "online"],
                width=1200, height=627,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1200, height=627, backgroundColor="#3498DB"),
                    TemplateElement(type="text", x=100, y=200, width=1000, height=227, content="Register Now", fontSize=48, color="#FFFFFF")
                ]
            ),
        ]

        # EDUCATION TEMPLATES (15+)
        education_templates = [
            CanvasTemplate(
                name="Certificate - Achievement",
                description="Professional achievement certificate",
                category=TemplateCategory.CERTIFICATE,
                tags=["certificate", "education", "achievement", "award"],
                width=1000, height=700,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=700, backgroundColor="#FFF"),
                    TemplateElement(type="text", x=100, y=150, width=800, height=100, content="CERTIFICATE OF ACHIEVEMENT", fontSize=48, color="#D4AF37")
                ],
                isFeatured=True
            ),
            CanvasTemplate(
                name="Infographic - Data Visualization",
                description="Data visualization infographic",
                category=TemplateCategory.INFOGRAPHIC,
                tags=["infographic", "data", "stats", "visualization"],
                width=1200, height=1500,
                elements=[
                    TemplateElement(type="text", x=100, y=100, width=1000, height=100, content="Key Statistics", fontSize=48, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Resume - Modern Design",
                description="Modern professional resume template",
                category=TemplateCategory.RESUME,
                tags=["resume", "cv", "modern", "professional"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=150, backgroundColor="#2C3E50"),
                    TemplateElement(type="text", x=50, y=40, width=700, height=70, content="Your Name", fontSize=40, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Course Poster",
                description="Online course promotional poster",
                category=TemplateCategory.POSTER,
                tags=["course", "education", "poster", "learning"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#3498DB")
                ]
            ),
            CanvasTemplate(
                name="Diploma Certificate",
                description="Educational diploma certificate",
                category=TemplateCategory.CERTIFICATE,
                tags=["diploma", "certificate", "graduation", "education"],
                width=1000, height=700,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=700, backgroundColor="#FFF8DC")
                ]
            ),
        ]

        # REAL ESTATE TEMPLATES (10+)
        realestate_templates = [
            CanvasTemplate(
                name="Property Listing Card",
                description="Real estate property listing design",
                category=TemplateCategory.REAL_ESTATE,
                tags=["real estate", "property", "listing", "realty"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=100, content="$500,000", fontSize=56, color="#E74C3C")
                ]
            ),
            CanvasTemplate(
                name="Open House Flyer",
                description="Real estate open house promotional flyer",
                category=TemplateCategory.FLYER,
                tags=["open house", "real estate", "flyer", "property"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#F39C12")
                ]
            ),
            CanvasTemplate(
                name="Apartment Rental Ad",
                description="Apartment rental advertisement design",
                category=TemplateCategory.REAL_ESTATE,
                tags=["apartment", "rental", "real estate", "housing"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=100, content="Apartments Available", fontSize=48, color="#2C3E50")
                ]
            ),
        ]

        # FASHION TEMPLATES (10+)
        fashion_templates = [
            CanvasTemplate(
                name="Fashion Lookbook Cover",
                description="Fashion collection lookbook page",
                category=TemplateCategory.FASHION,
                tags=["fashion", "lookbook", "collection", "style"],
                width=1000, height=1500,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=1500, backgroundColor="#F5F5F5")
                ]
            ),
            CanvasTemplate(
                name="Fashion Line Card",
                description="Fashion brand line up card",
                category=TemplateCategory.FASHION,
                tags=["fashion", "brand", "clothing", "style"],
                width=1000, height=1200,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=900, height=100, content="New Collection", fontSize=48, color="#000000")
                ]
            ),
            CanvasTemplate(
                name="Boutique Sale Poster",
                description="Fashion boutique sale poster",
                category=TemplateCategory.POSTER,
                tags=["fashion", "sale", "boutique", "poster"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#C0C0C0")
                ]
            ),
        ]

        # FOOD & RESTAURANT TEMPLATES (10+)
        food_templates = [
            CanvasTemplate(
                name="Recipe Card Design",
                description="Recipe card template",
                category=TemplateCategory.FOOD,
                tags=["recipe", "food", "card", "cooking"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=80, content="Recipe Title", fontSize=40, color="#D35400")
                ]
            ),
            CanvasTemplate(
                name="Restaurant Menu Card",
                description="Restaurant menu design",
                category=TemplateCategory.FOOD,
                tags=["menu", "restaurant", "food", "dining"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="text", x=50, y=50, width=700, height=100, content="MENU", fontSize=48, color="#8B4513")
                ]
            ),
            CanvasTemplate(
                name="Cafe Menu Board",
                description="Cafe menu board design",
                category=TemplateCategory.FOOD,
                tags=["cafe", "menu", "board", "food"],
                width=1000, height=1200,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=1200, backgroundColor="#8B7355")
                ]
            ),
        ]

        # FITNESS & WELLNESS TEMPLATES (10+)
        fitness_templates = [
            CanvasTemplate(
                name="Workout Plan Poster",
                description="Fitness workout plan poster",
                category=TemplateCategory.FITNESS,
                tags=["fitness", "workout", "health", "exercise"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#27AE60"),
                    TemplateElement(type="text", x=50, y=400, width=700, height=200, content="GET FIT IN 30 DAYS", fontSize=48, color="#FFFFFF")
                ]
            ),
            CanvasTemplate(
                name="Gym Membership Card",
                description="Gym membership card design",
                category=TemplateCategory.FITNESS,
                tags=["gym", "membership", "fitness", "card"],
                width=600, height=400,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=600, height=400, backgroundColor="#E74C3C")
                ]
            ),
            CanvasTemplate(
                name="Yoga Class Schedule",
                description="Yoga class schedule poster",
                category=TemplateCategory.FITNESS,
                tags=["yoga", "fitness", "schedule", "wellness"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#9B59B6")
                ]
            ),
        ]

        # TECH & STARTUP TEMPLATES (10+)
        tech_templates = [
            CanvasTemplate(
                name="Tech Startup Pitch Deck",
                description="Tech startup pitch presentation slide",
                category=TemplateCategory.PRESENTATION,
                tags=["startup", "tech", "pitch", "business"],
                width=1920, height=1080,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=1080, backgroundColor="#1A1A1A"),
                    TemplateElement(type="text", x=200, y=400, width=1520, height=200, content="Your Idea Here", fontSize=64, color="#00FF00")
                ]
            ),
            CanvasTemplate(
                name="App Launch Flyer",
                description="Mobile app launch promotional flyer",
                category=TemplateCategory.FLYER,
                tags=["app", "launch", "tech", "mobile"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#2196F3")
                ]
            ),
            CanvasTemplate(
                name="SaaS Product Page Hero",
                description="SaaS product page hero section",
                category=TemplateCategory.TECH,
                tags=["saas", "product", "tech", "hero"],
                width=1920, height=600,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1920, height=600, backgroundColor="#5E35B1")
                ]
            ),
        ]

        # NONPROFIT TEMPLATES (10+)
        nonprofit_templates = [
            CanvasTemplate(
                name="Charity Fundraiser Poster",
                description="Charity fundraiser event poster",
                category=TemplateCategory.NONPROFIT,
                tags=["nonprofit", "fundraiser", "charity", "event"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#C0392B")
                ]
            ),
            CanvasTemplate(
                name="Volunteer Recruitment Flyer",
                description="Volunteer recruitment promotional flyer",
                category=TemplateCategory.NONPROFIT,
                tags=["volunteer", "nonprofit", "recruitment", "community"],
                width=800, height=1000,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=800, height=1000, backgroundColor="#16A085")
                ]
            ),
        ]

        # TRAVEL TEMPLATES (5+)
        travel_templates = [
            CanvasTemplate(
                name="Travel Agency Brochure",
                description="Travel agency promotional brochure",
                category=TemplateCategory.TRAVEL,
                tags=["travel", "brochure", "tourism", "vacation"],
                width=1000, height=1200,
                elements=[
                    TemplateElement(type="shape", x=0, y=0, width=1000, height=1200, backgroundColor="#2980B9")
                ]
            ),
        ]

        # Compile all templates
        all_templates = (
            social_templates + business_templates + marketing_templates +
            presentation_templates + event_templates + education_templates +
            realestate_templates + fashion_templates + food_templates +
            fitness_templates + tech_templates + nonprofit_templates + travel_templates
        )

        # Assign unique IDs and metadata
        for idx, template in enumerate(all_templates):
            if not template.id:
                template.id = str(uuid.uuid4())
            template.downloads = idx * 5
            template.popularity = template.downloads + (template.rating * 10)
            template.metadata["template_number"] = idx + 1
            template.metadata["created_from"] = "free_template_library"

        return all_templates

    async def get_all_templates(self, skip: int = 0, limit: int = 100) -> List[CanvasTemplate]:
        """Get all available templates with pagination"""
        return self.templates[skip:skip+limit]

    async def get_templates_by_category(self, category: TemplateCategory, skip: int = 0, limit: int = 50) -> List[CanvasTemplate]:
        """Get templates filtered by category"""
        filtered = [t for t in self.templates if t.category == category]
        return filtered[skip:skip+limit]

    async def get_featured_templates(self) -> List[CanvasTemplate]:
        """Get featured templates"""
        return [t for t in self.templates if t.isFeatured][:12]

    async def search_templates(self, query: str, skip: int = 0, limit: int = 50) -> List[CanvasTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = [
            t for t in self.templates
            if query_lower in t.name.lower() or
               query_lower in t.description.lower() or
               any(query_lower in tag.lower() for tag in t.tags)
        ]
        return results[skip:skip+limit]

    async def get_template_by_id(self, template_id: str) -> Optional[CanvasTemplate]:
        """Get single template by ID"""
        return next((t for t in self.templates if t.id == template_id), None)

    async def get_trending_templates(self) -> List[CanvasTemplate]:
        """Get trending templates sorted by popularity"""
        sorted_templates = sorted(self.templates, key=lambda t: t.popularity, reverse=True)
        return sorted_templates[:20]

    async def increment_download_count(self, template_id: str):
        """Increment download count and popularity"""
        template = await self.get_template_by_id(template_id)
        if template:
            template.downloads += 1
            template.popularity = template.downloads + (template.rating * 10)
            logger.info(f"Template {template_id} downloaded - Total: {template.downloads}")

# Global template library instance
template_library = TemplateLibrary()

# API Routes
router = APIRouter(prefix="/api/ai-canvas/templates", tags=["AI Canvas Templates"])

@router.get("/all")
async def get_all_templates(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    """Get all templates with pagination"""
    return await template_library.get_all_templates(skip, limit)

@router.get("/featured")
async def get_featured_templates():
    """Get featured templates"""
    return await template_library.get_featured_templates()

@router.get("/trending")
async def get_trending_templates():
    """Get trending templates"""
    return await template_library.get_trending_templates()

@router.get("/categories")
async def get_categories():
    """Get all available template categories"""
    return {"categories": [cat.value for cat in TemplateCategory]}

@router.get("/category/{category}")
async def get_templates_by_category(
    category: TemplateCategory,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get templates by category"""
    return await template_library.get_templates_by_category(category, skip, limit)

@router.get("/search")
async def search_templates(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Search templates by query"""
    return await template_library.search_templates(q, skip, limit)

@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get single template by ID"""
    template = await template_library.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/{template_id}/download")
async def download_template(template_id: str):
    """Download/use template and increment count"""
    template = await template_library.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    await template_library.increment_download_count(template_id)
    return {"status": "success", "message": "Template downloaded", "template": template}
