from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=100)

class CheckoutRequest(BaseModel):
    items: List[CartItem] = Field(min_length=1)

class CheckoutResponse(BaseModel):
    order_id: int
    checkout_url: str

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    quantity: int
    unit_price: float

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total_amount: float
    status: str
    created_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
