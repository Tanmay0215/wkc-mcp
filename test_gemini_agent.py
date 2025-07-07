#!/usr/bin/env python3
"""
Test script for Gemini Agent natural language query processing
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8000"

def test_natural_language_queries():
    """Test various natural language queries"""
    
    print("🧪 Testing Gemini Agent Natural Language Queries")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        {
            "query": "Show me all my products",
            "user_id": "F0ha9ZavScbQm0TdJ3eHwv1aObJ3",
            "description": "Get seller products"
        },
        {
            "query": "Create a new product called Gaming Mouse for $50 with 10 in stock",
            "user_id": "F0ha9ZavScbQm0TdJ3eHwv1aObJ3",
            "description": "Create a new product"
        },
        {
            "query": "Search for electronics in my inventory",
            "user_id": "F0ha9ZavScbQm0TdJ3eHwv1aObJ3",
            "description": "Search products by category"
        },
        {
            "query": "Update the quantity of product ABC123 to 25",
            "description": "Update product quantity"
        },
        {
            "query": "Show me my recent orders",
            "user_id": "F0ha9ZavScbQm0TdJ3eHwv1aObJ3",
            "description": "Get user orders"
        },
        {
            "query": "What's the status of order ORD789?",
            "description": "Get order details"
        },
        {
            "query": "Delete product XYZ789 from my inventory",
            "description": "Delete a product"
        },
        {
            "query": "Tell me about the weather",
            "description": "Non-matching query (should return no function)"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        try:
            # Prepare request data
            data = {
                "query": test_case["query"]
            }
            
            if "user_id" in test_case:
                data["user_id"] = test_case["user_id"]
            
            # Make request
            response = requests.post(
                f"{BASE_URL}/query",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result["success"]:
                    print("✅ Success!")
                    print(f"Function called: {result.get('function_called', 'None')}")
                    print(f"Explanation: {result.get('explanation', 'None')}")
                    
                    if result.get("parameters_used"):
                        print(f"Parameters: {json.dumps(result['parameters_used'], indent=2)}")
                    
                    if result.get("result"):
                        print(f"Result: {json.dumps(result['result'], indent=2)}")
                else:
                    print("❌ Query failed")
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    print(f"Explanation: {result.get('explanation', 'None')}")
                    
                    if result.get("available_functions"):
                        print(f"Available functions: {result['available_functions']}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
        time.sleep(1)  # Small delay between requests

def test_specific_function_calls():
    """Test specific function calls to verify they work"""
    
    print("\n🔧 Testing Specific Function Calls")
    print("=" * 60)
    
    # Test creating a product
    print("\n📦 Creating a test product...")
    try:
        product_data = {
            "category": "Electronics",
            "companyName": "Test Company",
            "description": "A test gaming mouse for demonstration",
            "imageUrl": "https://example.com/mouse.jpg",
            "name": "Test Gaming Mouse",
            "price": 49.99,
            "quantity": 15,
            "sku": "TEST-MOUSE-001",
            "userType": "seller"
        }
        
        response = requests.post(
            f"{BASE_URL}/products",
            json=product_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                product_id = result["product_id"]
                print(f"✅ Product created with ID: {product_id}")
                
                # Test getting product details
                print(f"\n🔍 Getting product details for {product_id}...")
                response = requests.get(f"{BASE_URL}/products/{product_id}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        print("✅ Product details retrieved successfully")
                        print(f"Product: {result['product']['name']} - ${result['product']['price']}")
                    else:
                        print("❌ Failed to get product details")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
            else:
                print(f"❌ Failed to create product: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test server health check"""
    
    print("🏥 Testing Server Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Server is healthy!")
            print(f"Status: {result.get('status')}")
            print(f"Version: {result.get('version')}")
            print(f"Features: {', '.join(result.get('features', []))}")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 WKC MCP Server - Gemini Agent Test Suite")
    print("=" * 60)
    
    # Test health check first
    test_health_check()
    
    # Test specific function calls
    test_specific_function_calls()
    
    # Test natural language queries
    test_natural_language_queries()
    
    print("\n🎉 Test suite completed!")
    print("\n💡 Tips:")
    print("- Make sure your .env file has GEMINI_API_KEY set")
    print("- Ensure the server is running with: python main.py")
    print("- Check the server logs for detailed information")

if __name__ == "__main__":
    main() 