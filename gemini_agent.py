import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

from firebase_client import firebase_client
from models import ProductCreate, ProductUpdate

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiAgent:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Define available functions
        self.available_functions = {
            "get_seller_products": self._get_seller_products,
            "get_product_details": self._get_product_details,
            "create_product": self._create_product,
            "update_product": self._update_product,
            "delete_product": self._delete_product,
            "search_products": self._search_products,
            "update_product_quantity": self._update_product_quantity,
            "get_user_orders": self._get_user_orders,
            "get_order_details": self._get_order_details,
            "place_order": self._place_order,
            "update_order_status": self._update_order_status
        }
        
        # Function descriptions for the AI
        self.function_descriptions = [
            {
                "name": "get_seller_products",
                "description": "Get all products for a specific seller with pagination",
                "parameters": {
                    "user_id": "string - Seller's Firebase user ID",
                    "page": "integer - Page number (default: 1)",
                    "limit": "integer - Number of products per page (default: 10)"
                }
            },
            {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product",
                "parameters": {
                    "product_id": "string - Product ID to retrieve"
                }
            },
            {
                "name": "create_product",
                "description": "Create a new product for a seller",
                "parameters": {
                    "category": "string - Product category (e.g., Electronics, Clothing)",
                    "companyName": "string - Company name",
                    "description": "string - Product description",
                    "imageUrl": "string - Product image URL",
                    "name": "string - Product name",
                    "price": "number - Product price",
                    "quantity": "integer - Available quantity",
                    "sku": "string - Product SKU",
                    "userId": "string - Seller's Firebase user ID",
                    "userType": "string - User type (default: seller)"
                }
            },
            {
                "name": "update_product",
                "description": "Update an existing product's information",
                "parameters": {
                    "product_id": "string - Product ID to update",
                    "name": "string - New product name (optional)",
                    "price": "number - New price (optional)",
                    "quantity": "integer - New quantity (optional)",
                    "description": "string - New description (optional)",
                    "category": "string - New category (optional)",
                    "imageUrl": "string - New image URL (optional)"
                }
            },
            {
                "name": "delete_product",
                "description": "Delete a product from inventory",
                "parameters": {
                    "product_id": "string - Product ID to delete"
                }
            },
            {
                "name": "search_products",
                "description": "Search products for a seller by name, description, or SKU",
                "parameters": {
                    "user_id": "string - Seller's Firebase user ID",
                    "search_term": "string - Search term",
                    "category": "string - Category filter (optional)"
                }
            },
            {
                "name": "update_product_quantity",
                "description": "Update the quantity of a specific product",
                "parameters": {
                    "product_id": "string - Product ID",
                    "quantity": "integer - New quantity"
                }
            },
            {
                "name": "get_user_orders",
                "description": "Get all orders for a specific user",
                "parameters": {
                    "user_id": "string - User's Firebase user ID"
                }
            },
            {
                "name": "get_order_details",
                "description": "Get detailed information about a specific order",
                "parameters": {
                    "order_id": "string - Order ID to retrieve"
                }
            },
            {
                "name": "place_order",
                "description": "Place a new order via chat message",
                "parameters": {
                    "user_id": "string - Buyer's Firebase user ID",
                    "chat_message": "string - Order message",
                    "order_details": "object - Additional order details (optional)",
                    "use_ai_processing": "boolean - Whether to use AI processing (default: true)"
                }
            },
            {
                "name": "update_order_status",
                "description": "Update the status of an order",
                "parameters": {
                    "order_id": "string - Order ID",
                    "status": "string - New status (pending, processing, completed, cancelled)"
                }
            }
        ]
    
    def process_natural_language_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language query and convert it to a function call
        
        Args:
            query: Natural language query from user
            context: Additional context (user_id, etc.)
            
        Returns:
            Dict containing function call result and explanation
        """
        try:
            # Create system prompt for function calling
            system_prompt = self._create_system_prompt(context)
            
            # Create user prompt
            user_prompt = f"""
            User Query: "{query}"
            
            Based on the available functions and the user's query, determine which function to call and with what parameters.
            
            Available Functions:
            {json.dumps(self.function_descriptions, indent=2)}
            
            Please respond with a JSON object containing:
            {{
                "function_name": "name of the function to call",
                "parameters": {{
                    "param1": "value1",
                    "param2": "value2"
                }},
                "explanation": "Brief explanation of what this function will do"
            }}
            
            If the query doesn't match any function, respond with:
            {{
                "function_name": null,
                "parameters": {{}},
                "explanation": "No matching function found for this query"
            }}
            """
            
            # Get AI response
            response = self.model.generate_content(user_prompt)
            
            # Parse the response
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    return {
                        "success": False,
                        "error": "Failed to parse AI response",
                        "raw_response": response.text
                    }
            
            # Execute function if one was identified
            if result.get("function_name") and result["function_name"] in self.available_functions:
                function_name = result["function_name"]
                parameters = result.get("parameters", {})
                
                # Execute the function
                function_result = self.available_functions[function_name](**parameters)
                
                return {
                    "success": True,
                    "function_called": function_name,
                    "parameters": parameters,
                    "explanation": result.get("explanation", ""),
                    "result": function_result
                }
            else:
                return {
                    "success": False,
                    "function_called": None,
                    "explanation": result.get("explanation", "No matching function found"),
                    "available_functions": [f["name"] for f in self.function_descriptions]
                }
                
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                "success": False,
                "error": f"Failed to process query: {str(e)}"
            }
    
    def _create_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Create system prompt with context"""
        prompt = """
        You are an AI assistant for WKC (wkc.vercel.app) that helps users interact with their product inventory and orders through natural language.
        
        Your role is to:
        1. Understand user queries in natural language
        2. Identify the appropriate function to call
        3. Extract relevant parameters from the query
        4. Provide clear explanations of what will be done
        
        Context Information:
        """
        
        if context:
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        return prompt
    
    # Function implementations
    def _get_seller_products(self, user_id: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get seller's products"""
        try:
            result = firebase_client.get_seller_products(user_id, page, limit)
            return {
                "success": True,
                "data": result,
                "message": f"Retrieved {result['count']} products for seller"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        try:
            product = firebase_client.get_product_by_id(product_id)
            if product:
                return {
                    "success": True,
                    "data": product,
                    "message": f"Retrieved details for product {product_id}"
                }
            else:
                return {"success": False, "error": "Product not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_product(self, **kwargs) -> Dict[str, Any]:
        """Create a new product"""
        try:
            # Validate required fields
            required_fields = ["category", "companyName", "description", "imageUrl", "name", "price", "quantity", "sku", "userId"]
            for field in required_fields:
                if field not in kwargs:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Set default userType if not provided
            if "userType" not in kwargs:
                kwargs["userType"] = "seller"
            
            product_id = firebase_client.create_product(kwargs)
            return {
                "success": True,
                "data": {"product_id": product_id},
                "message": f"Product '{kwargs['name']}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_product(self, product_id: str, **kwargs) -> Dict[str, Any]:
        """Update a product"""
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return {"success": False, "error": "No valid update data provided"}
            
            success = firebase_client.update_product(product_id, update_data)
            if success:
                return {
                    "success": True,
                    "data": {"product_id": product_id},
                    "message": f"Product {product_id} updated successfully"
                }
            else:
                return {"success": False, "error": "Failed to update product"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_product(self, product_id: str) -> Dict[str, Any]:
        """Delete a product"""
        try:
            success = firebase_client.delete_product(product_id)
            if success:
                return {
                    "success": True,
                    "data": {"product_id": product_id},
                    "message": f"Product {product_id} deleted successfully"
                }
            else:
                return {"success": False, "error": "Failed to delete product"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _search_products(self, user_id: str, search_term: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Search products"""
        try:
            products = firebase_client.search_products(user_id, search_term, category)
            return {
                "success": True,
                "data": {"products": products, "count": len(products)},
                "message": f"Found {len(products)} products matching '{search_term}'"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_product_quantity(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Update product quantity"""
        try:
            success = firebase_client.update_product_quantity(product_id, quantity)
            if success:
                return {
                    "success": True,
                    "data": {"product_id": product_id, "quantity": quantity},
                    "message": f"Product quantity updated to {quantity}"
                }
            else:
                return {"success": False, "error": "Failed to update quantity"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_user_orders(self, user_id: str) -> Dict[str, Any]:
        """Get user orders"""
        try:
            orders = firebase_client.get_user_orders(user_id)
            return {
                "success": True,
                "data": {"orders": orders, "count": len(orders)},
                "message": f"Retrieved {len(orders)} orders for user"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        try:
            order = firebase_client.get_order_by_id(order_id)
            if order:
                return {
                    "success": True,
                    "data": order,
                    "message": f"Retrieved details for order {order_id}"
                }
            else:
                return {"success": False, "error": "Order not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _place_order(self, user_id: str, chat_message: str, order_details: Optional[Dict] = None, use_ai_processing: bool = True) -> Dict[str, Any]:
        """Place an order"""
        try:
            order_id = firebase_client.create_order(user_id, {
                "chat_message": chat_message,
                "order_details": order_details or {}
            })
            return {
                "success": True,
                "data": {"order_id": order_id},
                "message": f"Order placed successfully with ID: {order_id}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        try:
            success = firebase_client.update_order_status(order_id, status)
            if success:
                return {
                    "success": True,
                    "data": {"order_id": order_id, "status": status},
                    "message": f"Order status updated to {status}"
                }
            else:
                return {"success": False, "error": "Failed to update order status"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global Gemini Agent instance
gemini_agent = GeminiAgent() 