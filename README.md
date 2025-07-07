# WKC MCP Server with Gemini AI

A FastAPI-based Message Control Protocol (MCP) server for WKC (wkc.vercel.app) that handles order placement via chat messages using Firebase as the backend and Gemini AI for intelligent order processing.

## Features

- **AI-Powered Order Processing**: Uses Google's Gemini AI to intelligently extract order details from chat messages
- **Natural Language Queries**: Gemini Agent converts conversational queries to specific function calls
- **Order Placement via Chat**: Users can place orders by sending natural language chat messages from the frontend
- **Product Management**: Complete CRUD operations for product inventory management
- **Firebase Integration**: Uses Firebase Firestore for data storage
- **User Authentication**: Accepts Firebase user ID from authenticated frontend users
- **RESTful API**: Clean REST endpoints for order and product management
- **CORS Support**: Configured for cross-origin requests from the frontend
- **Error Handling**: Comprehensive error handling and logging
- **Order Modifications**: AI-powered order modification processing
- **Chat Processing**: Intelligent chat message analysis and intent detection

## Prerequisites

- Python 3.8+
- Firebase project with Firestore enabled
- Firebase service account key (JSON file)
- Google Gemini AI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wkc-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # Firebase Configuration
   FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-service-account.json
   FIREBASE_PROJECT_ID=your-firebase-project-id
   
   # Gemini AI Configuration
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # FastAPI Configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   
   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost:3000,https://wkc.vercel.app
   ```

4. **Set up Firebase**
   - Go to your Firebase Console
   - Navigate to Project Settings > Service Accounts
   - Generate a new private key (JSON file)
   - Save the JSON file as `firebase-service-account.json` in the project root
   - Enable Firestore in your Firebase project

5. **Get Gemini AI API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Running the Server

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Health Check
```
GET /
```
Returns server status and version information.

### 2. Natural Language Query Processing (Gemini Agent)
```
POST /query
```
Process natural language queries and convert them to specific function calls.

**Request Body:**
```json
{
  "query": "Show me all my products",
  "user_id": "optional_user_id",
  "context": {
    "additional_context": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "query": "Show me all my products",
  "function_called": "get_seller_products",
  "explanation": "This will retrieve all products for the specified seller",
  "parameters_used": {
    "user_id": "test_seller_123",
    "page": 1,
    "limit": 10
  },
  "result": {
    "success": true,
    "data": {
      "products": [...],
      "count": 5,
      "total_pages": 1,
      "current_page": 1
    },
    "message": "Retrieved 5 products for seller"
  }
}
```

**Example Queries:**
- "Show me all my products"
- "Create a new product called Gaming Mouse for $50"
- "Update the quantity of product ABC123 to 25"
- "Search for electronics in my inventory"
- "Show me my recent orders"

### 3. Place Order (AI-Enhanced)
```
POST /place_order
```
Place an order via chat message with AI processing.

**Request Body:**
```json
{
  "user_id": "firebase_user_id_here",
  "chat_message": "I want to order a large coffee and a croissant",
  "order_details": {
    "delivery_address": "123 Main St",
    "special_instructions": "Extra hot coffee"
  },
  "use_ai_processing": true
}
```

**Response:**
```json
{
  "success": true,
  "order_id": "generated_order_id",
  "message": "Order placed successfully",
  "data": {
    "user_id": "firebase_user_id_here",
    "chat_message": "I want to order a large coffee and a croissant",
    "order_details": {
      "items": [
        {"name": "large coffee", "quantity": 1},
        {"name": "croissant", "quantity": 1}
      ],
      "special_instructions": "Extra hot coffee",
      "delivery_preference": "delivery"
    }
  },
  "ai_processed": true,
  "ai_analysis": "Order contains 1 large coffee and 1 croissant with extra hot preference",
  "confirmation_message": "Thank you for your order! We've received your large coffee and croissant..."
}
```

### 3. Process Chat Message
```
POST /process_chat
```
Process a chat message with AI to extract intent and order details.

**Request Body:**
```json
{
  "user_id": "firebase_user_id_here",
  "message": "What's the status of my coffee order?",
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "processed_message": "What's the status of my coffee order?",
  "ai_response": "This appears to be a status inquiry about a coffee order.",
  "order_details": null,
  "intent": "conversation"
}
```

### 4. Modify Order (AI-Enhanced)
```
PUT /order/{order_id}/modify
```
Modify an existing order using AI processing.

**Request Body:**
```json
{
  "user_id": "firebase_user_id_here",
  "order_id": "order_id_here",
  "modification_message": "Can you add a sandwich to my order?"
}
```

### 5. Get User Orders
```
GET /user/{user_id}/orders
```
Get all orders for a specific user.

### 6. Get Order by ID
```
GET /order/{order_id}
```
Get a specific order by its ID.

### 7. Update Order Status
```
PUT /order/{order_id}/status
```
Update the status of an order.

## Testing

### Testing the Gemini Agent

Run the comprehensive test suite for the Gemini Agent:

```bash
python test_gemini_agent.py
```

This will test various natural language queries and demonstrate how the AI converts them to function calls.

### Example curl commands:

```bash
# Health check
curl http://localhost:8000/

# Natural language query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all my products",
    "user_id": "F0ha9ZavScbQm0TdJ3eHwv1aObJ3"
  }'

# Place an order
curl -X POST "http://localhost:8000/place_order" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "chat_message": "I want to order a large coffee and a croissant",
    "use_ai_processing": true
  }'

# Get user orders
curl http://localhost:8000/user/test_user_123/orders

# Process a chat message
curl -X POST "http://localhost:8000/process_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "message": "What is the status of my order?"
  }'

# Create a product
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Electronics",
    "companyName": "Test Company",
    "description": "A test product",
    "imageUrl": "https://example.com/image.jpg",
    "name": "Test Product",
    "price": 99.99,
    "quantity": 10,
    "sku": "TEST-001",
    "userType": "seller"
  }'
```

## Frontend Integration

### Example: Place Order with AI Processing

```javascript
// Place order with AI processing
const placeOrder = async (chatMessage, orderDetails = {}) => {
  try {
    const response = await fetch('http://localhost:8000/place_order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: firebaseUser.uid, // From Firebase Auth
        chat_message: chatMessage,
        order_details: orderDetails,
        use_ai_processing: true
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Order placed successfully:', result.order_id);
      console.log('AI Analysis:', result.ai_analysis);
      console.log('Confirmation:', result.confirmation_message);
      return result;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Error placing order:', error);
    throw error;
  }
};

// Usage
placeOrder('I want a large coffee and a croissant', {
  delivery_address: '123 Main St',
  special_instructions: 'Extra hot coffee'
});
```

### Example: Natural Language Query Processing

```javascript
// Process natural language queries
const processNaturalLanguageQuery = async (query, userId) => {
  try {
    const response = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        user_id: userId
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log(`Function called: ${result.function_called}`);
      console.log(`Explanation: ${result.explanation}`);
      console.log(`Result: ${JSON.stringify(result.result)}`);
      return result;
    } else {
      console.error(`Query failed: ${result.error}`);
      return result;
    }
  } catch (error) {
    console.error('Error processing query:', error);
    throw error;
  }
};

// Usage examples
processNaturalLanguageQuery("Show me all my products", "seller123");
processNaturalLanguageQuery("Create a new product called Gaming Mouse for $50", "seller123");
processNaturalLanguageQuery("Update the quantity of product ABC123 to 25", "seller123");
processNaturalLanguageQuery("Show me my recent orders", "buyer456");
```

### Example: Process Chat Message

```javascript
const processChatMessage = async (message) => {
  try {
    const response = await fetch('http://localhost:8000/process_chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: firebaseUser.uid,
        message: message,
        context: {}
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Intent:', result.intent);
      console.log('AI Response:', result.ai_response);
      
      if (result.intent === 'order' && result.order_details) {
        // Handle order intent
        console.log('Order details:', result.order_details);
      }
      
      return result;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Error processing chat:', error);
    throw error;
  }
};
```

## Firebase Data Structure

The server creates the following structure in Firestore:

```
orders/
  ├── {order_id}/
  │   ├── user_id: string
  │   ├── chat_message: string
  │   ├── order_details: object
  │   ├── ai_processed: boolean
  │   ├── ai_analysis: string
  │   ├── status: string (pending, processing, completed, cancelled, modified)
  │   ├── created_at: timestamp
  │   └── updated_at: timestamp
```

## AI Processing Features

### Order Extraction
- Automatically extracts items, quantities, and special instructions
- Identifies delivery/pickup preferences
- Handles natural language variations

### Intent Detection
- Distinguishes between order requests and general conversation
- Provides appropriate responses based on intent

### Order Modifications
- Processes modification requests in natural language
- Updates existing orders intelligently

### Confirmation Messages
- Generates friendly, personalized confirmation messages
- Includes order summary and next steps

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details"
}
```

Common HTTP status codes:
- `400`: Bad Request (missing required fields)
- `404`: Not Found (order not found)
- `500`: Internal Server Error

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` | Path to Firebase service account JSON | Yes | - |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes | - |
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes | - |
| `SECRET_KEY` | FastAPI secret key | No | Random string |
| `DEBUG` | Enable debug mode | No | False |
| `HOST` | Server host | No | 0.0.0.0 |
| `PORT` | Server port | No | 8000 |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | http://localhost:3000,https://wkc.vercel.app |

## Project Structure

```
wkc-mcp/
├── main.py                 # FastAPI application with AI integration
├── firebase_client.py      # Firebase integration
├── gemini_service.py       # Gemini AI service
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── Dockerfile            # Docker containerization
├── docker-compose.yml    # Docker Compose configuration
└── firebase-service-account.json  # Firebase credentials (not in repo)
```

## Deployment

### Docker (Recommended)

```bash
docker build -t wkc-mcp .
docker run -p 8000:8000 --env-file .env wkc-mcp
```

### Docker Compose

```bash
docker-compose up --build
```

## Security Considerations

1. **Firebase Security Rules**: Configure Firestore security rules to protect your data
2. **CORS**: Only allow necessary origins in production
3. **Rate Limiting**: Consider adding rate limiting for production use
4. **Input Validation**: All inputs are validated using Pydantic models
5. **Error Messages**: Avoid exposing sensitive information in error messages
6. **API Keys**: Keep your Gemini API key secure and never commit it to version control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 