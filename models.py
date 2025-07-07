from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class OrderItem(BaseModel):
    """Model for individual order items"""
    name: str = Field(..., description="Name of the item")
    quantity: int = Field(1, description="Quantity of the item")
    price: Optional[float] = Field(None, description="Price of the item")
    special_notes: Optional[str] = Field(None, description="Special notes for this item")

class Product(BaseModel):
    """Model for product data"""
    category: str = Field(..., description="Product category")
    companyName: str = Field(..., description="Company name")
    description: str = Field(..., description="Product description")
    imageUrl: str = Field(..., description="Product image URL")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Available quantity")
    sku: str = Field(..., description="Product SKU")
    userId: str = Field(..., description="Seller user ID")
    userType: str = Field("seller", description="User type")
    createdAt: Optional[str] = Field(None, description="Creation timestamp")
    updatedAt: Optional[str] = Field(None, description="Last update timestamp")

class ProductCreate(BaseModel):
    """Model for creating a new product"""
    category: str = Field(..., description="Product category")
    companyName: str = Field(..., description="Company name")
    description: str = Field(..., description="Product description")
    imageUrl: str = Field(..., description="Product image URL")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Available quantity")
    sku: str = Field(..., description="Product SKU")
    userType: str = Field("seller", description="User type")

class ProductUpdate(BaseModel):
    """Model for updating a product"""
    category: Optional[str] = Field(None, description="Product category")
    companyName: Optional[str] = Field(None, description="Company name")
    description: Optional[str] = Field(None, description="Product description")
    imageUrl: Optional[str] = Field(None, description="Product image URL")
    name: Optional[str] = Field(None, description="Product name")
    price: Optional[float] = Field(None, description="Product price")
    quantity: Optional[int] = Field(None, description="Available quantity")
    sku: Optional[str] = Field(None, description="Product SKU")

class ProductResponse(BaseModel):
    """Response model for product operations"""
    success: bool = Field(..., description="Operation success status")
    product_id: Optional[str] = Field(None, description="Product ID")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Product data")

class ProductsListResponse(BaseModel):
    """Response model for products list"""
    success: bool = Field(..., description="Operation success status")
    products: List[Dict[str, Any]] = Field(..., description="List of products")
    count: int = Field(..., description="Number of products")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")

class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language query")
    user_id: Optional[str] = Field(None, description="User ID for context")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")

class OrderRequest(BaseModel):
    """Request model for placing an order via chat"""
    user_id: str = Field(..., description="Firebase user ID from frontend")
    chat_message: str = Field(..., description="Chat message containing order details")
    order_details: Optional[Dict[str, Any]] = Field(default={}, description="Additional order details")
    use_ai_processing: bool = Field(True, description="Whether to use AI to process the chat message")

class OrderResponse(BaseModel):
    """Response model for order operations"""
    success: bool = Field(..., description="Operation success status")
    order_id: Optional[str] = Field(None, description="Created order ID")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")
    ai_processed: bool = Field(False, description="Whether AI processing was used")
    ai_analysis: Optional[str] = Field(None, description="AI analysis of the order")
    confirmation_message: Optional[str] = Field(None, description="AI-generated confirmation message")

class AIProcessedOrder(BaseModel):
    """Model for AI-processed order details"""
    items: List[OrderItem] = Field(default=[], description="List of ordered items")
    special_instructions: str = Field("", description="Special instructions for the order")
    delivery_preference: str = Field("not specified", description="Delivery or pickup preference")
    additional_requirements: str = Field("", description="Additional requirements")
    ai_analysis: str = Field("", description="AI analysis summary")

class OrderStatusUpdate(BaseModel):
    """Request model for updating order status"""
    status: str = Field(..., description="New order status")

class UserOrdersResponse(BaseModel):
    """Response model for user orders"""
    success: bool = Field(..., description="Operation success status")
    orders: list = Field(..., description="List of user orders")
    count: int = Field(..., description="Number of orders")

class OrderModificationRequest(BaseModel):
    """Request model for modifying an existing order"""
    user_id: str = Field(..., description="Firebase user ID")
    order_id: str = Field(..., description="Order ID to modify")
    modification_message: str = Field(..., description="Modification request message")

class OrderModificationResponse(BaseModel):
    """Response model for order modifications"""
    success: bool = Field(..., description="Operation success status")
    order_id: str = Field(..., description="Modified order ID")
    message: str = Field(..., description="Response message")
    original_order: Dict[str, Any] = Field(..., description="Original order details")
    updated_order: Dict[str, Any] = Field(..., description="Updated order details")
    modification_summary: str = Field(..., description="Summary of changes made")

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

class ChatMessageRequest(BaseModel):
    """Request model for processing chat messages with AI"""
    user_id: str = Field(..., description="Firebase user ID")
    message: str = Field(..., description="Chat message to process")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")

class ChatMessageResponse(BaseModel):
    """Response model for AI-processed chat messages"""
    success: bool = Field(..., description="Operation success status")
    processed_message: str = Field(..., description="Processed message")
    ai_response: str = Field(..., description="AI-generated response")
    order_details: Optional[AIProcessedOrder] = Field(None, description="Extracted order details if applicable")
    intent: str = Field("", description="Detected intent (order, question, etc.)") 