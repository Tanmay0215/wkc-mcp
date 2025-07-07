import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # System prompt for order processing
        self.system_prompt = """
        You are an AI assistant for WKC (wkc.vercel.app) that helps process orders from chat messages.
        
        Your role is to:
        1. Extract order details from user chat messages
        2. Structure the order information clearly
        3. Provide helpful responses to users
        4. Handle order modifications and clarifications
        
        When processing orders, extract:
        - Items ordered (with quantities if specified)
        - Special instructions or preferences
        - Delivery/pickup preferences
        - Any additional requirements
        
        Be friendly, helpful, and accurate in your responses.
        """
    
    def process_order_message(self, chat_message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a chat message to extract order details using Gemini AI
        
        Args:
            chat_message: The user's chat message
            user_id: Firebase user ID
            
        Returns:
            Dict containing processed order details
        """
        try:
            prompt = f"""
            {self.system_prompt}
            
            User ID: {user_id}
            Chat Message: "{chat_message}"
            
            Please analyze this order message and extract the following information:
            1. Items ordered (list each item with quantity)
            2. Special instructions or preferences
            3. Delivery/pickup preference
            4. Any additional requirements
            
            Format your response as a JSON object with these fields:
            - items: list of items with quantities
            - special_instructions: string
            - delivery_preference: string
            - additional_requirements: string
            - ai_analysis: brief summary of the order
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response and extract order details
            order_details = self._parse_ai_response(response.text, chat_message)
            
            return {
                "success": True,
                "order_details": order_details,
                "ai_analysis": order_details.get("ai_analysis", ""),
                "processed_message": chat_message
            }
            
        except Exception as e:
            logger.error(f"Error processing order message with Gemini: {e}")
            return {
                "success": False,
                "error": f"Failed to process order: {str(e)}",
                "order_details": {
                    "items": [],
                    "special_instructions": "",
                    "delivery_preference": "not specified",
                    "additional_requirements": "",
                    "ai_analysis": "Failed to process with AI"
                }
            }
    
    def _parse_ai_response(self, ai_response: str, original_message: str) -> Dict[str, Any]:
        """
        Parse the AI response and extract structured order details
        
        Args:
            ai_response: Raw AI response
            original_message: Original user message
            
        Returns:
            Structured order details
        """
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
                return {
                    "items": parsed_data.get("items", []),
                    "special_instructions": parsed_data.get("special_instructions", ""),
                    "delivery_preference": parsed_data.get("delivery_preference", "not specified"),
                    "additional_requirements": parsed_data.get("additional_requirements", ""),
                    "ai_analysis": parsed_data.get("ai_analysis", ai_response[:200])
                }
            else:
                # Fallback: create basic structure from AI response
                return {
                    "items": [{"name": "order from chat", "quantity": 1}],
                    "special_instructions": "",
                    "delivery_preference": "not specified",
                    "additional_requirements": "",
                    "ai_analysis": ai_response[:200]
                }
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "items": [{"name": "order from chat", "quantity": 1}],
                "special_instructions": "",
                "delivery_preference": "not specified",
                "additional_requirements": "",
                "ai_analysis": f"Original message: {original_message}"
            }
    
    def generate_order_confirmation(self, order_details: Dict[str, Any]) -> str:
        """
        Generate a confirmation message for the order
        
        Args:
            order_details: Processed order details
            
        Returns:
            Confirmation message
        """
        try:
            prompt = f"""
            Generate a friendly order confirmation message for the following order:
            
            Order Details: {order_details}
            
            The message should:
            1. Confirm the order was received
            2. Summarize the items ordered
            3. Mention any special instructions
            4. Provide next steps (order number, estimated time, etc.)
            5. Be friendly and professional
            
            Keep it concise but informative.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating confirmation: {e}")
            return "Thank you for your order! We've received it and will process it shortly."
    
    def handle_order_modification(self, original_order: Dict[str, Any], modification_request: str) -> Dict[str, Any]:
        """
        Handle order modification requests
        
        Args:
            original_order: Original order details
            modification_request: User's modification request
            
        Returns:
            Updated order details
        """
        try:
            prompt = f"""
            {self.system_prompt}
            
            Original Order: {original_order}
            Modification Request: "{modification_request}"
            
            Please analyze the modification request and provide updated order details.
            Return the complete updated order as a JSON object.
            """
            
            response = self.model.generate_content(prompt)
            updated_details = self._parse_ai_response(response.text, modification_request)
            
            return {
                "success": True,
                "updated_order": updated_details,
                "modification_summary": f"Order modified based on: {modification_request}"
            }
            
        except Exception as e:
            logger.error(f"Error handling order modification: {e}")
            return {
                "success": False,
                "error": f"Failed to process modification: {str(e)}"
            }

# Global Gemini service instance
gemini_service = GeminiService() 