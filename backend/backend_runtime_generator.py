"""
BACKEND RUNTIME GENERATOR - Express.js / FastAPI Generation
Transforms GAAIUS blueprints into real API servers with proper structure
Part of the GAAIUS Project Runtime System
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class BackendRuntimeGenerator:
    """Generates Express.js or FastAPI applications from GAAIUS blueprints"""
    
    def generate_from_blueprint(self, blueprint: Dict[str, Any], project_path: Path, backend_type: str = "express") -> Dict[str, str]:
        """
        Generate backend from a GAAIUS blueprint
        
        Args:
            blueprint: GAAIUS blueprint dictionary
            project_path: Path where to generate files
            backend_type: "express" or "fastapi"
            
        Returns:
            Dict of created files and their content
        """
        if backend_type == "express":
            return self._generate_express_backend(blueprint, project_path)
        else:
            return self._generate_fastapi_backend(blueprint, project_path)
    
    def _generate_express_backend(self, blueprint: Dict[str, Any], project_path: Path) -> Dict[str, str]:
        """Generate Express.js backend"""
        files = {}
        
        # Generate routes based on features
        routes = self._generate_express_routes(blueprint)
        files.update(routes)
        
        # Generate models
        models = self._generate_models(blueprint)
        files.update(models)
        
        # Generate services
        services = self._generate_express_services(blueprint)
        files.update(services)
        
        # Generate middleware
        files["src/middleware/validation.ts"] = self._template_express_validation_middleware()
        files["src/middleware/errorHandler.ts"] = self._template_express_error_handler()
        
        # Generate config
        files["src/config/database.ts"] = self._template_express_database_config(blueprint)
        
        # Write files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    def _generate_fastapi_backend(self, blueprint: Dict[str, Any], project_path: Path) -> Dict[str, str]:
        """Generate FastAPI backend"""
        files = {}
        
        # Generate routes based on features
        routes = self._generate_fastapi_routes(blueprint)
        files.update(routes)
        
        # Generate models
        models = self._generate_models(blueprint, language="python")
        files.update(models)
        
        # Generate schemas
        schemas = self._generate_fastapi_schemas(blueprint)
        files.update(schemas)
        
        # Generate services
        services = self._generate_fastapi_services(blueprint)
        files.update(services)
        
        # Generate config
        files["app/config.py"] = self._template_fastapi_config(blueprint)
        
        # Write files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    def _generate_express_routes(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Express routes from blueprint"""
        files = {}
        features = blueprint.get("features", [])
        
        # Base routes
        files["src/routes/index.ts"] = self._template_express_routes_index(features)
        
        # Feature-specific routes
        if "auth" in features:
            files["src/routes/auth.ts"] = self._template_express_auth_routes()
        
        if "cart" in features or "ecommerce" in blueprint.get("app_type", ""):
            files["src/routes/products.ts"] = self._template_express_products_routes()
            files["src/routes/orders.ts"] = self._template_express_orders_routes()
        
        if "search" in features:
            files["src/routes/search.ts"] = self._template_express_search_routes()
        
        if "profile" in features or "user" in features:
            files["src/routes/users.ts"] = self._template_express_users_routes()
        
        if "dashboard" in features or "admin" in features:
            files["src/routes/dashboard.ts"] = self._template_express_dashboard_routes()
        
        return files
    
    def _generate_fastapi_routes(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate FastAPI routes from blueprint"""
        files = {}
        features = blueprint.get("features", [])
        
        files["app/routers/__init__.py"] = ""
        
        if "auth" in features:
            files["app/routers/auth.py"] = self._template_fastapi_auth_routes()
        
        if "cart" in features or "ecommerce" in blueprint.get("app_type", ""):
            files["app/routers/products.py"] = self._template_fastapi_products_routes()
            files["app/routers/orders.py"] = self._template_fastapi_orders_routes()
        
        if "search" in features:
            files["app/routers/search.py"] = self._template_fastapi_search_routes()
        
        if "profile" in features or "user" in features:
            files["app/routers/users.py"] = self._template_fastapi_users_routes()
        
        if "dashboard" in features or "admin" in features:
            files["app/routers/dashboard.py"] = self._template_fastapi_dashboard_routes()
        
        return files
    
    def _generate_models(self, blueprint: Dict[str, Any], language: str = "ts") -> Dict[str, str]:
        """Generate data models"""
        files = {}
        app_type = blueprint.get("app_type", "web")
        
        if language == "ts":
            # Express/TypeORM models
            if "auth" in blueprint.get("features", []) or "user" in blueprint.get("features", []):
                files["src/models/User.ts"] = self._template_express_user_model()
            
            if "ecommerce" in app_type:
                files["src/models/Product.ts"] = self._template_express_product_model()
                files["src/models/Order.ts"] = self._template_express_order_model()
            
            if "dashboard" in app_type or "admin" in blueprint.get("features", []):
                files["src/models/Analytics.ts"] = self._template_express_analytics_model()
        else:
            # FastAPI/SQLAlchemy models
            files["app/models/__init__.py"] = ""
            
            if "auth" in blueprint.get("features", []) or "user" in blueprint.get("features", []):
                files["app/models/user.py"] = self._template_fastapi_user_model()
            
            if "ecommerce" in app_type:
                files["app/models/product.py"] = self._template_fastapi_product_model()
                files["app/models/order.py"] = self._template_fastapi_order_model()
        
        return files
    
    def _generate_express_services(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Express services"""
        files = {}
        features = blueprint.get("features", [])
        app_type = blueprint.get("app_type", "")
        
        if "auth" in features:
            files["src/services/AuthService.ts"] = self._template_express_auth_service()
        
        if "ecommerce" in app_type:
            files["src/services/ProductService.ts"] = self._template_express_product_service()
            files["src/services/OrderService.ts"] = self._template_express_order_service()
        
        if "search" in features:
            files["src/services/SearchService.ts"] = self._template_express_search_service()
        
        return files
    
    def _generate_fastapi_services(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate FastAPI services"""
        files = {}
        features = blueprint.get("features", [])
        app_type = blueprint.get("app_type", "")
        
        files["app/services/__init__.py"] = ""
        
        if "auth" in features:
            files["app/services/auth_service.py"] = self._template_fastapi_auth_service()
        
        if "ecommerce" in app_type:
            files["app/services/product_service.py"] = self._template_fastapi_product_service()
            files["app/services/order_service.py"] = self._template_fastapi_order_service()
        
        if "search" in features:
            files["app/services/search_service.py"] = self._template_fastapi_search_service()
        
        return files
    
    def _generate_fastapi_schemas(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate FastAPI Pydantic schemas"""
        files = {}
        
        files["app/schemas/__init__.py"] = ""
        files["app/schemas/user.py"] = self._template_fastapi_user_schema()
        
        if "ecommerce" in blueprint.get("app_type", ""):
            files["app/schemas/product.py"] = self._template_fastapi_product_schema()
            files["app/schemas/order.py"] = self._template_fastapi_order_schema()
        
        return files
    
    # ===== EXPRESS TEMPLATES =====
    
    def _template_express_routes_index(self, features: List[str]) -> str:
        """Express main routes file"""
        imports = []
        uses = []
        
        if "auth" in features:
            imports.append("import authRoutes from './auth'")
            uses.append("router.use('/auth', authRoutes)")
        
        if "cart" in features:
            imports.append("import productRoutes from './products'")
            uses.append("router.use('/products', productRoutes)")
        
        if "user" in features:
            imports.append("import userRoutes from './users'")
            uses.append("router.use('/users', userRoutes)")
        
        imports_str = "\n".join(imports)
        uses_str = "\n".join(uses)
        
        return f"""import {{ Router }} from 'express'
{imports_str}

const router = Router()

router.get('/health', (req, res) => {{
  res.json({{ status: 'ok', timestamp: new Date() }})
}})

{uses_str}

export default router
"""
    
    def _template_express_auth_routes(self) -> str:
        """Express auth routes"""
        return """import { Router } from 'express'
import AuthService from '../services/AuthService'

const router = Router()

router.post('/register', async (req, res, next) => {
  try {
    const { email, password, name } = req.body
    const result = await AuthService.register(email, password, name)
    res.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body
    const result = await AuthService.login(email, password)
    res.json(result)
  } catch (error) {
    next(error)
  }
})

router.post('/logout', (req, res) => {
  res.json({ message: 'Logged out successfully' })
})

router.get('/me', (req, res) => {
  // Requires auth middleware
  res.json(req.user)
})

export default router
"""
    
    def _template_express_products_routes(self) -> str:
        """Express products routes"""
        return """import { Router } from 'express'
import ProductService from '../services/ProductService'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const { skip = 0, limit = 20, search } = req.query
    const products = await ProductService.getProducts(
      parseInt(skip as string),
      parseInt(limit as string),
      search as string
    )
    res.json(products)
  } catch (error) {
    next(error)
  }
})

router.get('/:id', async (req, res, next) => {
  try {
    const product = await ProductService.getProductById(req.params.id)
    if (!product) {
      return res.status(404).json({ error: 'Product not found' })
    }
    res.json(product)
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const product = await ProductService.createProduct(req.body)
    res.status(201).json(product)
  } catch (error) {
    next(error)
  }
})

export default router
"""
    
    def _template_express_orders_routes(self) -> str:
        """Express orders routes"""
        return """import { Router } from 'express'
import OrderService from '../services/OrderService'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const orders = await OrderService.getOrders(req.user.id)
    res.json(orders)
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const order = await OrderService.createOrder(req.user.id, req.body)
    res.status(201).json(order)
  } catch (error) {
    next(error)
  }
})

router.get('/:id', async (req, res, next) => {
  try {
    const order = await OrderService.getOrderById(req.params.id, req.user.id)
    if (!order) {
      return res.status(404).json({ error: 'Order not found' })
    }
    res.json(order)
  } catch (error) {
    next(error)
  }
})

export default router
"""
    
    def _template_express_search_routes(self) -> str:
        """Express search routes"""
        return """import { Router } from 'express'
import SearchService from '../services/SearchService'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const { q, type = 'all' } = req.query
    if (!q) {
      return res.status(400).json({ error: 'Query parameter required' })
    }
    const results = await SearchService.search(q as string, type as string)
    res.json(results)
  } catch (error) {
    next(error)
  }
})

export default router
"""
    
    def _template_express_users_routes(self) -> str:
        """Express users routes"""
        return """import { Router } from 'express'

const router = Router()

router.get('/:id', async (req, res) => {
  res.json({
    id: req.params.id,
    name: 'User',
    email: 'user@example.com'
  })
})

router.put('/:id', async (req, res) => {
  res.json({
    id: req.params.id,
    ...req.body,
    updated_at: new Date()
  })
})

export default router
"""
    
    def _template_express_dashboard_routes(self) -> str:
        """Express dashboard routes"""
        return """import { Router } from 'express'

const router = Router()

router.get('/stats', async (req, res) => {
  res.json({
    total_users: 1234,
    total_revenue: 45231,
    total_orders: 523,
    conversion_rate: 0.032
  })
})

router.get('/analytics', async (req, res) => {
  res.json({
    daily_revenue: [],
    user_activity: [],
    top_products: []
  })
})

export default router
"""
    
    def _template_express_user_model(self) -> str:
        """Express User model"""
        return """import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm'

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column({ unique: true })
  email: string

  @Column()
  name: string

  @Column()
  password: string

  @Column({ nullable: true })
  avatar?: string

  @CreateDateColumn()
  createdAt: Date

  @Column({ default: false })
  isVerified: boolean
}
"""
    
    def _template_express_product_model(self) -> str:
        """Express Product model"""
        return """import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm'

@Entity('products')
export class Product {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column()
  name: string

  @Column({ type: 'text' })
  description: string

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number

  @Column({ default: 0 })
  stock: number

  @Column({ nullable: true })
  image?: string

  @CreateDateColumn()
  createdAt: Date
}
"""
    
    def _template_express_order_model(self) -> str:
        """Express Order model"""
        return """import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne } from 'typeorm'
import { User } from './User'

@Entity('orders')
export class Order {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @ManyToOne(() => User)
  user: User

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  total: number

  @Column({ default: 'pending' })
  status: string

  @Column({ type: 'json' })
  items: any[]

  @CreateDateColumn()
  createdAt: Date
}
"""
    
    def _template_express_analytics_model(self) -> str:
        """Express Analytics model"""
        return """import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm'

@Entity('analytics')
export class Analytics {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column()
  event: string

  @Column({ nullable: true })
  userId?: string

  @Column({ type: 'json', nullable: true })
  metadata?: any

  @CreateDateColumn()
  createdAt: Date
}
"""
    
    def _template_express_auth_service(self) -> str:
        """Express Auth service"""
        return """import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'

class AuthService {
  async register(email: string, password: string, name: string) {
    // TODO: Check if user exists
    // TODO: Hash password
    // TODO: Save to database
    const hashedPassword = await bcrypt.hash(password, 10)
    return {
      user: { email, name },
      message: 'User registered successfully'
    }
  }

  async login(email: string, password: string) {
    // TODO: Find user by email
    // TODO: Compare password
    // TODO: Generate token
    const token = jwt.sign(
      { email },
      process.env.JWT_SECRET || 'secret',
      { expiresIn: '24h' }
    )
    return { token, user: { email } }
  }

  verifyToken(token: string) {
    return jwt.verify(token, process.env.JWT_SECRET || 'secret')
  }
}

export default new AuthService()
"""
    
    def _template_express_product_service(self) -> str:
        """Express Product service"""
        return """class ProductService {
  async getProducts(skip: number = 0, limit: number = 20, search?: string) {
    // TODO: Query database
    return {
      data: [],
      total: 0,
      skip,
      limit
    }
  }

  async getProductById(id: string) {
    // TODO: Query database
    return null
  }

  async createProduct(data: any) {
    // TODO: Save to database
    return { id: '1', ...data }
  }

  async updateProduct(id: string, data: any) {
    // TODO: Update in database
    return { id, ...data }
  }

  async deleteProduct(id: string) {
    // TODO: Delete from database
    return { success: true }
  }
}

export default new ProductService()
"""
    
    def _template_express_order_service(self) -> str:
        """Express Order service"""
        return """class OrderService {
  async getOrders(userId: string) {
    // TODO: Query database for user orders
    return []
  }

  async getOrderById(id: string, userId: string) {
    // TODO: Query database
    return null
  }

  async createOrder(userId: string, data: any) {
    // TODO: Save to database
    return { id: '1', userId, ...data }
  }

  async updateOrderStatus(id: string, status: string) {
    // TODO: Update in database
    return { id, status }
  }
}

export default new OrderService()
"""
    
    def _template_express_search_service(self) -> str:
        """Express Search service"""
        return """class SearchService {
  async search(query: string, type: string = 'all') {
    // TODO: Search across different entities
    return {
      products: [],
      users: [],
      orders: [],
      query,
      type
    }
  }
}

export default new SearchService()
"""
    
    def _template_express_validation_middleware(self) -> str:
        """Express validation middleware"""
        return """import { Request, Response, NextFunction } from 'express'
import { z } from 'zod'

export function validateRequest(schema: z.ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      schema.parse(req.body)
      next()
    } catch (error) {
      res.status(400).json({ error: 'Validation failed', details: error })
    }
  }
}
"""
    
    def _template_express_error_handler(self) -> str:
        """Express error handler middleware"""
        return """import { Request, Response, NextFunction } from 'express'

export default function errorHandler(
  error: any,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error('Error:', error)

  const status = error.status || 500
  const message = error.message || 'Internal server error'

  res.status(status).json({
    error: message,
    status,
    ...(process.env.DEBUG && { stack: error.stack })
  })
}
"""
    
    def _template_express_database_config(self, blueprint: Dict[str, Any]) -> str:
        """Express database configuration"""
        return """import { DataSource } from 'typeorm'
import { User } from '../models/User'

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USER || 'user',
  password: process.env.DB_PASSWORD || 'password',
  database: process.env.DB_NAME || 'myapp',
  synchronize: process.env.NODE_ENV === 'development',
  logging: true,
  entities: [User],
})
"""
    
    # ===== FASTAPI TEMPLATES =====
    
    def _template_fastapi_auth_routes(self) -> str:
        """FastAPI auth routes"""
        return """from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    # TODO: Hash password and save to database
    return {
        "user": {"email": data.email, "name": data.name},
        "message": "User registered successfully"
    }

@router.post("/login")
async def login(data: LoginRequest):
    # TODO: Verify credentials
    # TODO: Generate JWT token
    return {
        "token": "jwt_token_here",
        "user": {"email": data.email}
    }

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
"""
    
    def _template_fastapi_products_routes(self) -> str:
        """FastAPI products routes"""
        return """from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def list_products(skip: int = Query(0), limit: int = Query(20), search: str = None):
    # TODO: Query database
    return {
        "data": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }

@router.get("/{product_id}")
async def get_product(product_id: str):
    # TODO: Query database
    return {}

@router.post("/", status_code=201)
async def create_product(data: dict):
    # TODO: Save to database
    return {"id": "1", **data}
"""
    
    def _template_fastapi_orders_routes(self) -> str:
        """FastAPI orders routes"""
        return """from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
async def list_orders():
    # TODO: Query user orders
    return []

@router.get("/{order_id}")
async def get_order(order_id: str):
    # TODO: Query database
    return {}

@router.post("/", status_code=201)
async def create_order(data: dict):
    # TODO: Save to database
    return {"id": "1", **data}
"""
    
    def _template_fastapi_search_routes(self) -> str:
        """FastAPI search routes"""
        return """from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def search(q: str = Query(..., min_length=1), type: str = "all"):
    # TODO: Search across entities
    return {
        "products": [],
        "users": [],
        "orders": [],
        "query": q,
        "type": type
    }
"""
    
    def _template_fastapi_users_routes(self) -> str:
        """FastAPI users routes"""
        return """from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {
        "id": user_id,
        "name": "User",
        "email": "user@example.com"
    }

@router.put("/{user_id}")
async def update_user(user_id: str, data: dict):
    return {
        "id": user_id,
        **data,
        "updated_at": "2024-01-22T00:00:00Z"
    }
"""
    
    def _template_fastapi_dashboard_routes(self) -> str:
        """FastAPI dashboard routes"""
        return """from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_stats():
    return {
        "total_users": 1234,
        "total_revenue": 45231,
        "total_orders": 523,
        "conversion_rate": 0.032
    }

@router.get("/analytics")
async def get_analytics():
    return {
        "daily_revenue": [],
        "user_activity": [],
        "top_products": []
    }
"""
    
    def _template_fastapi_user_model(self) -> str:
        """FastAPI User model"""
        return """from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
    
    def _template_fastapi_product_model(self) -> str:
        """FastAPI Product model"""
        return """from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
    
    def _template_fastapi_order_model(self) -> str:
        """FastAPI Order model"""
        return """from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    total = Column(Float, nullable=False)
    status = Column(String, default="pending")
    items = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
    
    def _template_fastapi_user_schema(self) -> str:
        """FastAPI User Pydantic schema"""
        return """from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
"""
    
    def _template_fastapi_product_schema(self) -> str:
        """FastAPI Product Pydantic schema"""
        return """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 0
    image: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
"""
    
    def _template_fastapi_order_schema(self) -> str:
        """FastAPI Order Pydantic schema"""
        return """from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemSchema(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItemSchema]

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total: float
    status: str
    items: List[OrderItemSchema]
    created_at: datetime

    class Config:
        from_attributes = True
"""
    
    def _template_fastapi_auth_service(self) -> str:
        """FastAPI Auth service"""
        return """import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

class AuthService:
    @staticmethod
    async def register(email: str, password: str, name: str):
        # TODO: Check if user exists
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        # TODO: Save to database
        return {"user": {"email": email, "name": name}}

    @staticmethod
    async def login(email: str, password: str) -> Optional[str]:
        # TODO: Find user by email
        # TODO: Verify password
        token = jwt.encode(
            {"email": email, "exp": datetime.utcnow() + timedelta(hours=24)},
            "secret",
            algorithm="HS256"
        )
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, "secret", algorithms=["HS256"])
        except:
            return None
"""
    
    def _template_fastapi_product_service(self) -> str:
        """FastAPI Product service"""
        return """class ProductService:
    @staticmethod
    async def get_products(skip: int = 0, limit: int = 20, search: Optional[str] = None):
        # TODO: Query database
        return {"data": [], "total": 0}

    @staticmethod
    async def get_product_by_id(product_id: str):
        # TODO: Query database
        return None

    @staticmethod
    async def create_product(data: dict):
        # TODO: Save to database
        return {"id": "1", **data}
"""
    
    def _template_fastapi_order_service(self) -> str:
        """FastAPI Order service"""
        return """class OrderService:
    @staticmethod
    async def get_orders(user_id: str):
        # TODO: Query database
        return []

    @staticmethod
    async def create_order(user_id: str, data: dict):
        # TODO: Save to database
        return {"id": "1", "user_id": user_id, **data}

    @staticmethod
    async def update_order_status(order_id: str, status: str):
        # TODO: Update in database
        return {"id": order_id, "status": status}
"""
    
    def _template_fastapi_search_service(self) -> str:
        """FastAPI Search service"""
        return """from typing import Optional

class SearchService:
    @staticmethod
    async def search(query: str, type: str = "all"):
        # TODO: Search across entities
        return {
            "products": [],
            "users": [],
            "orders": [],
            "query": query,
            "type": type
        }
"""
    
    def _template_fastapi_config(self, blueprint: Dict[str, Any]) -> str:
        """FastAPI configuration"""
        return """import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # JWT
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY: int = 86400
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
"""
