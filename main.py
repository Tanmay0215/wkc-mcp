import os
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any

from firebase_client import firebase_client
from gemini_service import gemini_service
from gemini_agent import gemini_agent
from models import (
    OrderRequest, 
    OrderResponse, 
    OrderStatusUpdate, 
    UserOrdersResponse, 
    ErrorResponse,
    OrderModificationRequest,
    OrderModificationResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    AIProcessedOrder,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductsListResponse,
    NaturalLanguageQueryRequest
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WKC MCP Server with Gemini AI",
    description="Message Control Protocol server for WKC order management powered by Gemini AI",
    version="2.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://wkc.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Firebase is already initialized in firebase_client.py
        # Gemini AI is already initialized in gemini_service.py
        # Gemini Agent is already initialized in gemini_agent.py
        logger.info("WKC MCP Server with Gemini AI started successfully")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "WKC MCP Server with Gemini AI is running",
        "status": "healthy",
        "version": "2.0.0",
        "features": ["order_processing", "ai_chat", "firebase_integration", "product_management", "natural_language_queries"]
    }

# Natural Language Query Endpoint
@app.post("/query")
async def process_natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Process natural language queries and convert them to function calls
    
    This endpoint allows users to interact with the system using natural language.
    The AI will automatically determine which function to call based on the query.
    
    Examples:
    - "Show me all my products"
    - "Create a new product called Gaming Mouse for $50"
    - "Update the quantity of product ABC123 to 25"
    - "Search for electronics in my inventory"
    - "Show me my recent orders"
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Add user_id to context if provided
        context = request.context or {}
        if request.user_id:
            context["user_id"] = request.user_id
        
        # Process the query with Gemini Agent
        result = gemini_agent.process_natural_language_query(request.query, context)
        
        if result["success"]:
            return {
                "success": True,
                "query": request.query,
                "function_called": result.get("function_called"),
                "explanation": result.get("explanation"),
                "result": result.get("result"),
                "parameters_used": result.get("parameters", {})
            }
        else:
            return {
                "success": False,
                "query": request.query,
                "error": result.get("error"),
                "explanation": result.get("explanation"),
                "available_functions": result.get("available_functions", [])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

# Product Management Routes
@app.post("/products", response_model=ProductResponse)
async def create_product(product_data: ProductCreate):
    """
    Create a new product for a seller
    
    This endpoint allows sellers to add new products to their inventory.
    """
    try:
        # Validate required fields
        if not product_data.name.strip():
            raise HTTPException(status_code=400, detail="Product name is required")
        
        if product_data.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        if product_data.quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        # Create product in Firebase
        product_data_dict = product_data.dict()
        product_id = firebase_client.create_product(product_data_dict)
        
        logger.info(f"Product created successfully with ID: {product_id}")
        
        return ProductResponse(
            success=True,
            product_id=product_id,
            message="Product created successfully",
            data=product_data.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.get("/products/seller/{user_id}", response_model=ProductsListResponse)
async def get_seller_products(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Products per page")
):
    """
    Get all products for a specific seller with pagination
    
    Args:
        user_id: Seller user ID
        page: Page number (1-based)
        limit: Number of products per page
    """
    try:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="User ID is required")
        
        result = firebase_client.get_seller_products(user_id, page, limit)
        
        return ProductsListResponse(
            success=True,
            products=result['products'],
            count=result['count'],
            total_pages=result['total_pages'],
            current_page=result['current_page']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching seller products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch seller products: {str(e)}")

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """
    Get a specific product by ID
    
    Args:
        product_id: Product ID
    """
    try:
        if not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        product = firebase_client.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "success": True,
            "product": product,
            "message": "Product retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, update_data: ProductUpdate):
    """
    Update a product
    
    Args:
        product_id: Product ID
        update_data: Product update data
    """
    try:
        if not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        # Remove None values from update data
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid update data provided")
        
        # Validate price if provided
        if 'price' in update_dict and update_dict['price'] <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        # Validate quantity if provided
        if 'quantity' in update_dict and update_dict['quantity'] < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        success = firebase_client.update_product(product_id, update_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update product")
        
        # Get updated product
        updated_product = firebase_client.get_product_by_id(product_id)
        
        return ProductResponse(
            success=True,
            product_id=product_id,
            message="Product updated successfully",
            data=updated_product
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """
    Delete a product
    
    Args:
        product_id: Product ID
    """
    try:
        if not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        success = firebase_client.delete_product(product_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete product")
        
        return {
            "success": True,
            "message": f"Product {product_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")

@app.get("/products/seller/{user_id}/search")
async def search_seller_products(
    user_id: str,
    search_term: str = Query(..., description="Search term"),
    category: str = Query(None, description="Category filter")
):
    """
    Search products for a seller
    
    Args:
        user_id: Seller user ID
        search_term: Search term
        category: Optional category filter
    """
    try:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if not search_term.strip():
            raise HTTPException(status_code=400, detail="Search term is required")
        
        products = firebase_client.search_products(user_id, search_term, category)
        
        return {
            "success": True,
            "products": products,
            "count": len(products),
            "search_term": search_term,
            "category": category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search products: {str(e)}")

@app.put("/products/{product_id}/quantity")
async def update_product_quantity(
    product_id: str,
    quantity: int = Query(..., ge=0, description="New quantity")
):
    """
    Update product quantity for inventory management
    
    Args:
        product_id: Product ID
        quantity: New quantity
    """
    try:
        if not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        success = firebase_client.update_product_quantity(product_id, quantity)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update product quantity")
        
        return {
            "success": True,
            "message": f"Product quantity updated to {quantity}",
            "product_id": product_id,
            "quantity": quantity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product quantity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update product quantity: {str(e)}")

# Order Management Routes (existing)
@app.post("/place_order", response_model=OrderResponse)
async def place_order(order_request: OrderRequest):
    """
    Place an order via chat message with AI processing
    
    This endpoint accepts a Firebase user ID and chat message from the frontend,
    processes it with Gemini AI, and creates an order in Firebase Firestore.
    """
    try:
        # Validate user_id is not empty
        if not order_request.user_id.strip():
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Validate chat_message is not empty
        if not order_request.chat_message.strip():
            raise HTTPException(status_code=400, detail="Chat message is required")
        
        ai_processed = False
        ai_analysis = None
        confirmation_message = None
        processed_order_details = order_request.order_details or {}
        
        # Process with AI if enabled
        if order_request.use_ai_processing:
            try:
                ai_result = gemini_service.process_order_message(
                    order_request.chat_message, 
                    order_request.user_id
                )
                
                if ai_result["success"]:
                    ai_processed = True
                    ai_analysis = ai_result.get("ai_analysis", "")
                    processed_order_details.update(ai_result.get("order_details", {}))
                    
                    # Generate confirmation message
                    confirmation_message = gemini_service.generate_order_confirmation(
                        processed_order_details
                    )
                else:
                    logger.warning(f"AI processing failed: {ai_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error in AI processing: {e}")
                # Continue without AI processing
        
        # Create order in Firebase
        order_id = firebase_client.create_order(
            user_id=order_request.user_id,
            order_data={
                "chat_message": order_request.chat_message,
                "order_details": processed_order_details,
                "ai_processed": ai_processed,
                "ai_analysis": ai_analysis
            }
        )
        
        logger.info(f"Order placed successfully for user {order_request.user_id} with ID: {order_id}")
        
        return OrderResponse(
            success=True,
            order_id=order_id,
            message="Order placed successfully",
            data={
                "user_id": order_request.user_id,
                "chat_message": order_request.chat_message,
                "order_details": processed_order_details
            },
            ai_processed=ai_processed,
            ai_analysis=ai_analysis,
            confirmation_message=confirmation_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@app.post("/process_chat", response_model=ChatMessageResponse)
async def process_chat_message(chat_request: ChatMessageRequest):
    """
    Process a chat message with AI to extract intent and order details
    
    This endpoint uses Gemini AI to analyze chat messages and determine
    if they contain order information or other intents.
    """
    try:
        if not chat_request.user_id.strip():
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if not chat_request.message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process with AI
        ai_result = gemini_service.process_order_message(
            chat_request.message, 
            chat_request.user_id
        )
        
        if ai_result["success"]:
            order_details = ai_result.get("order_details", {})
            
            # Determine intent based on AI analysis
            intent = "order" if order_details.get("items") else "conversation"
            
            return ChatMessageResponse(
                success=True,
                processed_message=chat_request.message,
                ai_response=ai_result.get("ai_analysis", ""),
                order_details=AIProcessedOrder(**order_details) if order_details else None,
                intent=intent
            )
        else:
            raise HTTPException(status_code=500, detail=ai_result.get("error", "AI processing failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")

@app.put("/order/{order_id}/modify", response_model=OrderModificationResponse)
async def modify_order(order_id: str, modification_request: OrderModificationRequest):
    """
    Modify an existing order using AI processing
    
    This endpoint allows users to modify their orders by sending
    a modification request that gets processed by Gemini AI.
    """
    try:
        if not order_id.strip():
            raise HTTPException(status_code=400, detail="Order ID is required")
        
        # Get original order
        original_order = firebase_client.get_order_by_id(order_id)
        if not original_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Process modification with AI
        modification_result = gemini_service.handle_order_modification(
            original_order,
            modification_request.modification_message
        )
        
        if modification_result["success"]:
            updated_order = modification_result["updated_order"]
            
            # Update order in Firebase
            success = firebase_client.update_order_status(order_id, "modified")
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update order")
            
            return OrderModificationResponse(
                success=True,
                order_id=order_id,
                message="Order modified successfully",
                original_order=original_order,
                updated_order=updated_order,
                modification_summary=modification_result["modification_summary"]
            )
        else:
            raise HTTPException(status_code=500, detail=modification_result.get("error", "Modification failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error modifying order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to modify order: {str(e)}")

@app.get("/user/{user_id}/orders", response_model=UserOrdersResponse)
async def get_user_orders(user_id: str):
    """
    Get all orders for a specific user
    
    Args:
        user_id: Firebase user ID
    """
    try:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="User ID is required")
        
        orders = firebase_client.get_user_orders(user_id)
        
        # Convert datetime objects to strings for JSON serialization
        for order in orders:
            if 'created_at' in order:
                order['created_at'] = order['created_at'].isoformat()
            if 'updated_at' in order:
                order['updated_at'] = order['updated_at'].isoformat()
        
        return UserOrdersResponse(
            success=True,
            orders=orders,
            count=len(orders)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user orders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user orders: {str(e)}")

@app.get("/order/{order_id}")
async def get_order(order_id: str):
    """
    Get a specific order by ID
    
    Args:
        order_id: Order ID
    """
    try:
        if not order_id.strip():
            raise HTTPException(status_code=400, detail="Order ID is required")
        
        order = firebase_client.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Convert datetime objects to strings for JSON serialization
        if 'created_at' in order:
            order['created_at'] = order['created_at'].isoformat()
        if 'updated_at' in order:
            order['updated_at'] = order['updated_at'].isoformat()
        
        return {
            "success": True,
            "order": order,
            "message": "Order retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")

@app.put("/order/{order_id}/status")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    """
    Update order status
    
    Args:
        order_id: Order ID
        status_update: New status
    """
    try:
        if not order_id.strip():
            raise HTTPException(status_code=400, detail="Order ID is required")
        
        success = firebase_client.update_order_status(order_id, status_update.status)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update order status")
        
        return {
            "success": True,
            "message": f"Order status updated to {status_update.status}",
            "order_id": order_id,
            "status": status_update.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for HTTP errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            details=f"HTTP {exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom exception handler for general errors"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            details=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 