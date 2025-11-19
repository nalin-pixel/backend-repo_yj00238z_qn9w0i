"""
Database Schemas for the shop

Each Pydantic model maps to a MongoDB collection. Collection name
is the lowercase class name (e.g., Product -> "product").
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-friendly unique identifier")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category name")
    images: List[HttpUrl] = Field(default_factory=list, description="Image URLs")
    materials: Optional[List[str]] = Field(default=None, description="Materials used")
    dimensions: Optional[str] = Field(default=None, description="Dimensions / size notes")
    in_stock: bool = Field(True, description="Whether product is available")
    stock_qty: Optional[int] = Field(default=None, ge=0, description="If tracked, how many available")
    featured: bool = Field(False, description="Showcase on landing")
    sustainable_tags: Optional[List[str]] = Field(default=None, description="Sustainability tags")

class OrderItem(BaseModel):
    slug: str
    title: str
    price: float
    quantity: int = Field(1, ge=1)

class Order(BaseModel):
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str
    created_at: Optional[datetime] = None
