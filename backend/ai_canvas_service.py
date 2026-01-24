import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import aiofiles
from PIL import Image, ImageDraw, ImageFont
import io
import os
from pathlib import Path
import logging
from enum import Enum
import hashlib
import base64
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ShapeType(str, Enum):
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    LINE = "line"
    POLYGON = "polygon"
    STAR = "star"

class ElementType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    SHAPE = "shape"
    GROUP = "group"
    PATH = "path"

class ExportFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    PDF = "pdf"
    SVG = "svg"
    WEBP = "webp"

class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"
    CONIC = "conic"

class ColorStop(BaseModel):
    position: float = Field(..., ge=0, le=100)
    color: str

class Gradient(BaseModel):
    type: GradientType
    angle: Optional[int] = 0
    stops: List[ColorStop]

class Transform(BaseModel):
    x: float = 0
    y: float = 0
    scaleX: float = 1
    scaleY: float = 1
    rotation: float = 0
    skewX: float = 0
    skewY: float = 0

class Shadow(BaseModel):
    offsetX: float = 0
    offsetY: float = 0
    blur: float = 0
    spread: float = 0
    color: str = "#000000"
    opacity: float = 1

class Stroke(BaseModel):
    width: float = 0
    color: str = "#000000"
    opacity: float = 1
    lineCap: str = "round"
    lineJoin: str = "round"
    dashArray: Optional[List[float]] = None

class Fill(BaseModel):
    type: str = "solid"
    color: Optional[str] = None
    gradient: Optional[Gradient] = None
    opacity: float = 1

class TextProperties(BaseModel):
    content: str
    fontSize: float = 16
    fontFamily: str = "Arial"
    fontWeight: int = 400
    fontStyle: str = "normal"
    letterSpacing: float = 0
    lineHeight: float = 1.2
    textAlign: str = "left"
    textDecoration: str = "none"
    color: str = "#000000"
    opacity: float = 1

class ShapeProperties(BaseModel):
    shapeType: ShapeType
    width: float = 100
    height: float = 100
    cornerRadius: float = 0
    sides: Optional[int] = None

class ImageProperties(BaseModel):
    url: str
    width: float = 200
    height: float = 200
    preserveAspectRatio: bool = True
    cropX: float = 0
    cropY: float = 0
    cropWidth: Optional[float] = None
    cropHeight: Optional[float] = None

class CanvasElement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ElementType
    name: str = ""
    zIndex: int = 0
    visible: bool = True
    locked: bool = False
    blendMode: str = "normal"
    opacity: float = 1
    transform: Transform = Field(default_factory=Transform)
    fill: Fill = Field(default_factory=Fill)
    stroke: Optional[Stroke] = None
    shadow: Optional[Shadow] = None
    textProperties: Optional[TextProperties] = None
    shapeProperties: Optional[ShapeProperties] = None
    imageProperties: Optional[ImageProperties] = None
    children: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class CanvasPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Page 1"
    width: float = 1920
    height: float = 1080
    elements: List[CanvasElement] = Field(default_factory=list)
    backgroundColor: str = "#ffffff"
    backgroundOpacity: float = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class CanvasHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    userId: str = ""

class AICanvasDesign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    title: str
    description: Optional[str] = None
    pages: List[CanvasPage] = Field(default_factory=list)
    thumbnail: Optional[str] = None
    history: List[CanvasHistory] = Field(default_factory=list)
    historyIndex: int = -1
    tags: List[str] = Field(default_factory=list)
    version: int = 1
    locked: bool = False
    shared: bool = False
    sharedWith: List[str] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastModifiedBy: str = ""

class ExportRequest(BaseModel):
    format: ExportFormat
    pageId: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    dpi: int = 72
    background: Optional[str] = None
    quality: int = 95

class AICanvasService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.designs_collection = db.ai_canvas_designs
        self.assets_collection = db.ai_canvas_assets
        self.history_max_size = 100
        self.cache = {}

    async def create_design(self, user_id: str, title: str, description: Optional[str] = None) -> AICanvasDesign:
        design = AICanvasDesign(
            userId=user_id,
            title=title,
            description=description,
            pages=[CanvasPage()]
        )
        
        result = await self.designs_collection.insert_one(design.dict(by_alias=True))
        design.id = str(result.inserted_id)
        return design

    async def get_design(self, design_id: str, user_id: str) -> AICanvasDesign:
        doc = await self.designs_collection.find_one({
            "_id": design_id,
            "userId": user_id
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Design not found")
        return AICanvasDesign(**doc)

    async def list_designs(self, user_id: str, skip: int = 0, limit: int = 20) -> List[AICanvasDesign]:
        cursor = self.designs_collection.find({
            "userId": user_id
        }).skip(skip).limit(limit).sort("updatedAt", -1)
        
        designs = []
        async for doc in cursor:
            designs.append(AICanvasDesign(**doc))
        return designs

    async def update_design(self, design_id: str, user_id: str, updates: Dict[str, Any]) -> AICanvasDesign:
        updates["updatedAt"] = datetime.utcnow()
        updates["lastModifiedBy"] = user_id
        
        result = await self.designs_collection.find_one_and_update(
            {"_id": design_id, "userId": user_id},
            {"$set": updates},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Design not found")
        return AICanvasDesign(**result)

    async def add_page(self, design_id: str, user_id: str, page_name: str = "New Page") -> CanvasPage:
        design = await self.get_design(design_id, user_id)
        new_page = CanvasPage(name=page_name)
        
        design.pages.append(new_page)
        await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})
        
        return new_page

    async def delete_page(self, design_id: str, user_id: str, page_id: str) -> AICanvasDesign:
        design = await self.get_design(design_id, user_id)
        design.pages = [p for p in design.pages if p.id != page_id]
        
        if not design.pages:
            design.pages = [CanvasPage()]
        
        return await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})

    async def add_element(self, design_id: str, user_id: str, page_id: str, element: CanvasElement) -> CanvasElement:
        design = await self.get_design(design_id, user_id)
        page = next((p for p in design.pages if p.id == page_id), None)
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page.elements.append(element)
        await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})
        
        return element

    async def update_element(self, design_id: str, user_id: str, page_id: str, element_id: str, updates: Dict[str, Any]) -> CanvasElement:
        design = await self.get_design(design_id, user_id)
        page = next((p for p in design.pages if p.id == page_id), None)
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        element = next((e for e in page.elements if e.id == element_id), None)
        if not element:
            raise HTTPException(status_code=404, detail="Element not found")
        
        for key, value in updates.items():
            if hasattr(element, key):
                setattr(element, key, value)
        
        element.updatedAt = datetime.utcnow()
        await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})
        
        return element

    async def delete_element(self, design_id: str, user_id: str, page_id: str, element_id: str) -> AICanvasDesign:
        design = await self.get_design(design_id, user_id)
        page = next((p for p in design.pages if p.id == page_id), None)
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page.elements = [e for e in page.elements if e.id != element_id]
        await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})
        
        return design

    async def duplicate_element(self, design_id: str, user_id: str, page_id: str, element_id: str) -> CanvasElement:
        design = await self.get_design(design_id, user_id)
        page = next((p for p in design.pages if p.id == page_id), None)
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        element = next((e for e in page.elements if e.id == element_id), None)
        if not element:
            raise HTTPException(status_code=404, detail="Element not found")
        
        duplicated = CanvasElement(**element.dict())
        duplicated.id = str(uuid.uuid4())
        duplicated.transform.x += 20
        duplicated.transform.y += 20
        
        page.elements.append(duplicated)
        await self.update_design(design_id, user_id, {"pages": [p.dict() for p in design.pages]})
        
        return duplicated

    async def undo(self, design_id: str, user_id: str) -> AICanvasDesign:
        design = await self.get_design(design_id, user_id)
        
        if design.historyIndex > 0:
            design.historyIndex -= 1
            history_state = design.history[design.historyIndex]
            
            await self.update_design(design_id, user_id, {
                "pages": history_state.after.get("pages", []),
                "historyIndex": design.historyIndex
            })
        
        return design

    async def redo(self, design_id: str, user_id: str) -> AICanvasDesign:
        design = await self.get_design(design_id, user_id)
        
        if design.historyIndex < len(design.history) - 1:
            design.historyIndex += 1
            history_state = design.history[design.historyIndex]
            
            await self.update_design(design_id, user_id, {
                "pages": history_state.after.get("pages", []),
                "historyIndex": design.historyIndex
            })
        
        return design

    async def add_to_history(self, design_id: str, user_id: str, action: str, before: Dict[str, Any], after: Dict[str, Any]):
        design = await self.get_design(design_id, user_id)
        
        history_entry = CanvasHistory(
            action=action,
            before=before,
            after=after,
            userId=user_id
        )
        
        design.history = design.history[:design.historyIndex + 1]
        design.history.append(history_entry)
        design.historyIndex = len(design.history) - 1
        
        if len(design.history) > self.history_max_size:
            design.history = design.history[-self.history_max_size:]
            design.historyIndex = len(design.history) - 1
        
        await self.update_design(design_id, user_id, {
            "history": [h.dict() for h in design.history],
            "historyIndex": design.historyIndex
        })

    async def export_design(self, design_id: str, user_id: str, export_request: ExportRequest) -> bytes:
        design = await self.get_design(design_id, user_id)
        
        if export_request.pageId:
            page = next((p for p in design.pages if p.id == export_request.pageId), None)
        else:
            page = design.pages[0]
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        width = export_request.width or int(page.width)
        height = export_request.height or int(page.height)
        
        if export_request.format == ExportFormat.PNG:
            return await self._render_to_png(page, width, height, export_request.background)
        elif export_request.format == ExportFormat.JPEG:
            return await self._render_to_jpeg(page, width, height, export_request.background, export_request.quality)
        elif export_request.format == ExportFormat.SVG:
            return await self._render_to_svg(page)
        elif export_request.format == ExportFormat.PDF:
            return await self._render_to_pdf(page, width, height, export_request.background)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    async def _render_to_png(self, page: CanvasPage, width: int, height: int, background: Optional[str] = None) -> bytes:
        img = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))
        
        if background:
            try:
                bg_color = background.lstrip("#")
                r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
                img = Image.new("RGB", (width, height), color=(r, g, b))
            except:
                pass
        
        for element in sorted(page.elements, key=lambda e: e.zIndex):
            await self._render_element(img, element, width, height)
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    async def _render_to_jpeg(self, page: CanvasPage, width: int, height: int, background: Optional[str] = None, quality: int = 95) -> bytes:
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        
        if background:
            try:
                bg_color = background.lstrip("#")
                r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
                img = Image.new("RGB", (width, height), color=(r, g, b))
            except:
                pass
        
        for element in sorted(page.elements, key=lambda e: e.zIndex):
            await self._render_element(img, element, width, height)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        return buffer.getvalue()

    async def _render_to_svg(self, page: CanvasPage) -> bytes:
        svg_content = f'<svg width="{page.width}" height="{page.height}" xmlns="http://www.w3.org/2000/svg">'
        svg_content += f'<rect width="{page.width}" height="{page.height}" fill="{page.backgroundColor}"/>'
        
        for element in sorted(page.elements, key=lambda e: e.zIndex):
            svg_content += self._element_to_svg(element)
        
        svg_content += '</svg>'
        return svg_content.encode()

    async def _render_to_pdf(self, page: CanvasPage, width: int, height: int, background: Optional[str] = None) -> bytes:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import landscape
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
        
        if background:
            try:
                bg_color = background.lstrip("#")
                r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
                c.setFillColor((r/255, g/255, b/255))
                c.rect(0, 0, width, height, fill=1)
            except:
                pass
        
        for element in sorted(page.elements, key=lambda e: e.zIndex):
            await self._render_element_pdf(c, element, width, height)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    async def _render_element(self, img: Image.Image, element: CanvasElement, width: int, height: int):
        if element.type == ElementType.TEXT and element.textProperties:
            self._render_text_element(img, element, width, height)
        elif element.type == ElementType.SHAPE and element.shapeProperties:
            self._render_shape_element(img, element, width, height)
        elif element.type == ElementType.IMAGE and element.imageProperties:
            await self._render_image_element(img, element, width, height)

    def _render_text_element(self, img: Image.Image, element: CanvasElement, width: int, height: int):
        draw = ImageDraw.Draw(img)
        props = element.textProperties
        
        x = int(element.transform.x)
        y = int(element.transform.y)
        
        try:
            font_size = int(props.fontSize)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        color = props.color
        if color.startswith("#"):
            color_hex = color.lstrip("#")
            color_tuple = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_tuple = (0, 0, 0)
        
        draw.text((x, y), props.content, font=font, fill=color_tuple)

    def _render_shape_element(self, img: Image.Image, element: CanvasElement, width: int, height: int):
        draw = ImageDraw.Draw(img)
        props = element.shapeProperties
        
        x1 = int(element.transform.x)
        y1 = int(element.transform.y)
        x2 = x1 + int(props.width)
        y2 = y1 + int(props.height)
        
        fill_color = element.fill.color if element.fill.color else None
        outline_color = element.stroke.color if element.stroke else None
        
        if props.shapeType == ShapeType.RECTANGLE:
            draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color)
        elif props.shapeType == ShapeType.CIRCLE:
            draw.ellipse([x1, y1, x2, y2], fill=fill_color, outline=outline_color)
        elif props.shapeType == ShapeType.TRIANGLE:
            points = [(x1, y2), ((x1 + x2) // 2, y1), (x2, y2)]
            draw.polygon(points, fill=fill_color, outline=outline_color)

    async def _render_image_element(self, img: Image.Image, element: CanvasElement, width: int, height: int):
        props = element.imageProperties
        
        try:
            import requests
            response = requests.get(props.url, timeout=5)
            asset_img = Image.open(io.BytesIO(response.content))
            
            if element.transform.scaleX != 1 or element.transform.scaleY != 1:
                new_width = int(props.width * element.transform.scaleX)
                new_height = int(props.height * element.transform.scaleY)
                asset_img = asset_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                asset_img = asset_img.resize((int(props.width), int(props.height)), Image.Resampling.LANCZOS)
            
            x = int(element.transform.x)
            y = int(element.transform.y)
            img.paste(asset_img, (x, y), asset_img if asset_img.mode == "RGBA" else None)
        except Exception as e:
            logger.error(f"Failed to render image: {e}")

    async def _render_element_pdf(self, c, element: CanvasElement, width: int, height: int):
        if element.type == ElementType.TEXT and element.textProperties:
            props = element.textProperties
            c.drawString(int(element.transform.x), int(element.transform.y), props.content)

    def _element_to_svg(self, element: CanvasElement) -> str:
        if element.type == ElementType.TEXT and element.textProperties:
            props = element.textProperties
            return f'<text x="{element.transform.x}" y="{element.transform.y}" font-size="{props.fontSize}" fill="{props.color}">{props.content}</text>'
        elif element.type == ElementType.SHAPE and element.shapeProperties:
            props = element.shapeProperties
            fill = element.fill.color or "white"
            
            if props.shapeType == ShapeType.RECTANGLE:
                return f'<rect x="{element.transform.x}" y="{element.transform.y}" width="{props.width}" height="{props.height}" fill="{fill}"/>'
            elif props.shapeType == ShapeType.CIRCLE:
                cx = element.transform.x + props.width / 2
                cy = element.transform.y + props.height / 2
                r = props.width / 2
                return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
        return ""

    async def upload_asset(self, user_id: str, file: UploadFile) -> Dict[str, str]:
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = f"assets/{user_id}/{file_id}{file_ext}"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        await self.assets_collection.insert_one({
            "_id": file_id,
            "userId": user_id,
            "filename": file.filename,
            "path": file_path,
            "size": len(content),
            "uploadedAt": datetime.utcnow()
        })
        
        return {"assetId": file_id, "path": file_path}

    async def share_design(self, design_id: str, user_id: str, share_with: List[str]) -> AICanvasDesign:
        design = await self.get_design(design_id, user_id)
        design.shared = True
        design.sharedWith = list(set(design.sharedWith + share_with))
        
        return await self.update_design(design_id, user_id, {
            "shared": design.shared,
            "sharedWith": design.sharedWith
        })

    async def delete_design(self, design_id: str, user_id: str):
        result = await self.designs_collection.delete_one({
            "_id": design_id,
            "userId": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Design not found")
        
        return {"message": "Design deleted successfully"}

router = APIRouter(prefix="/api/ai-canvas", tags=["AI Canvas"])

_db_instance = None

def get_db() -> AsyncIOMotorDatabase:
    return _db_instance

@router.post("/designs")
async def create_design(
    title: str,
    description: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.create_design("user_id", title, description)

@router.get("/designs")
async def list_designs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[AICanvasDesign]:
    service = AICanvasService(db)
    return await service.list_designs("user_id", skip, limit)

@router.get("/designs/{design_id}")
async def get_design(
    design_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.get_design(design_id, "user_id")

@router.put("/designs/{design_id}")
async def update_design(
    design_id: str,
    updates: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.update_design(design_id, "user_id", updates)

@router.delete("/designs/{design_id}")
async def delete_design(
    design_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    service = AICanvasService(db)
    return await service.delete_design(design_id, "user_id")

@router.post("/designs/{design_id}/pages")
async def add_page(
    design_id: str,
    page_name: str = "New Page",
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CanvasPage:
    service = AICanvasService(db)
    return await service.add_page(design_id, "user_id", page_name)

@router.delete("/designs/{design_id}/pages/{page_id}")
async def delete_page(
    design_id: str,
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.delete_page(design_id, "user_id", page_id)

@router.post("/designs/{design_id}/pages/{page_id}/elements")
async def add_element(
    design_id: str,
    page_id: str,
    element: CanvasElement,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CanvasElement:
    service = AICanvasService(db)
    return await service.add_element(design_id, "user_id", page_id, element)

@router.put("/designs/{design_id}/pages/{page_id}/elements/{element_id}")
async def update_element(
    design_id: str,
    page_id: str,
    element_id: str,
    updates: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CanvasElement:
    service = AICanvasService(db)
    return await service.update_element(design_id, "user_id", page_id, element_id, updates)

@router.delete("/designs/{design_id}/pages/{page_id}/elements/{element_id}")
async def delete_element(
    design_id: str,
    page_id: str,
    element_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.delete_element(design_id, "user_id", page_id, element_id)

@router.post("/designs/{design_id}/pages/{page_id}/elements/{element_id}/duplicate")
async def duplicate_element(
    design_id: str,
    page_id: str,
    element_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CanvasElement:
    service = AICanvasService(db)
    return await service.duplicate_element(design_id, "user_id", page_id, element_id)

@router.post("/designs/{design_id}/undo")
async def undo(
    design_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.undo(design_id, "user_id")

@router.post("/designs/{design_id}/redo")
async def redo(
    design_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.redo(design_id, "user_id")

@router.post("/designs/{design_id}/export")
async def export_design(
    design_id: str,
    export_request: ExportRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> StreamingResponse:
    service = AICanvasService(db)
    content = await service.export_design(design_id, "user_id", export_request)
    
    format_ext = export_request.format.value
    return StreamingResponse(
        iter([content]),
        media_type=f"image/{format_ext}" if format_ext != "pdf" else "application/pdf",
        headers={"Content-Disposition": f"attachment; filename=design.{format_ext}"}
    )

@router.post("/designs/{design_id}/share")
async def share_design(
    design_id: str,
    share_with: List[str],
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AICanvasDesign:
    service = AICanvasService(db)
    return await service.share_design(design_id, "user_id", share_with)

@router.post("/assets/upload")
async def upload_asset(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Dict[str, str]:
    service = AICanvasService(db)
    return await service.upload_asset("user_id", file)
