import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

class FirebaseClient:
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase with service account credentials"""
        try:
            # Get the path to the service account key file
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
            
            if not service_account_path or not os.path.exists(service_account_path):
                raise FileNotFoundError(f"Firebase service account key file not found at: {service_account_path}")
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise
    
    # Product Management Methods
    def create_product(self, product_data: Dict[str, Any]) -> str:
        """
        Create a new product in Firestore
        
        Args:
            product_data: Product information
            
        Returns:
            str: Product ID
        """
        try:
            # Add timestamps
            current_time = datetime.utcnow().isoformat() + "Z"
            product_data['createdAt'] = current_time
            product_data['updatedAt'] = current_time
            
            # Add to Firestore
            product_ref = self.db.collection('products').add(product_data)
            product_id = product_ref[1].id
            
            print(f"Product created successfully with ID: {product_id}")
            return product_id
            
        except Exception as e:
            print(f"Error creating product: {e}")
            raise
    
    def get_seller_products(self, user_id: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Get all products for a specific seller with pagination
        
        Args:
            user_id: Seller user ID
            page: Page number (1-based)
            limit: Number of products per page
            
        Returns:
            Dict containing products and pagination info
        """
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get products for the seller
            products_ref = self.db.collection('products').where('userId', '==', user_id)
            
            # Get total count
            total_products = len(list(products_ref.stream()))
            
            # Get paginated results
            products = []
            for doc in products_ref.limit(limit).offset(offset).stream():
                product_data = doc.to_dict()
                product_data['id'] = doc.id
                products.append(product_data)
            
            total_pages = (total_products + limit - 1) // limit
            
            return {
                'products': products,
                'count': len(products),
                'total_count': total_products,
                'total_pages': total_pages,
                'current_page': page,
                'limit': limit
            }
            
        except Exception as e:
            print(f"Error fetching seller products: {e}")
            raise
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Optional[Dict]: Product data or None if not found
        """
        try:
            product_ref = self.db.collection('products').document(product_id)
            product_doc = product_ref.get()
            
            if product_doc.exists:
                product_data = product_doc.to_dict()
                product_data['id'] = product_doc.id
                return product_data
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching product: {e}")
            return None
    
    def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a product
        
        Args:
            product_id: Product ID to update
            update_data: Data to update
            
        Returns:
            bool: Success status
        """
        try:
            # Add updated timestamp
            update_data['updatedAt'] = datetime.utcnow().isoformat() + "Z"
            
            product_ref = self.db.collection('products').document(product_id)
            product_ref.update(update_data)
            
            print(f"Product {product_id} updated successfully")
            return True
            
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product
        
        Args:
            product_id: Product ID to delete
            
        Returns:
            bool: Success status
        """
        try:
            product_ref = self.db.collection('products').document(product_id)
            product_ref.delete()
            
            print(f"Product {product_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def search_products(self, user_id: str, search_term: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search products for a seller
        
        Args:
            user_id: Seller user ID
            search_term: Search term
            category: Optional category filter
            
        Returns:
            List of matching products
        """
        try:
            # Start with seller's products
            products_ref = self.db.collection('products').where('userId', '==', user_id)
            
            products = []
            for doc in products_ref.stream():
                product_data = doc.to_dict()
                product_data['id'] = doc.id
                
                # Check if product matches search criteria
                matches_search = (
                    search_term.lower() in product_data.get('name', '').lower() or
                    search_term.lower() in product_data.get('description', '').lower() or
                    search_term.lower() in product_data.get('sku', '').lower()
                )
                
                matches_category = not category or product_data.get('category', '') == category
                
                if matches_search and matches_category:
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            print(f"Error searching products: {e}")
            raise
    
    def update_product_quantity(self, product_id: str, new_quantity: int) -> bool:
        """
        Update product quantity (for inventory management)
        
        Args:
            product_id: Product ID
            new_quantity: New quantity
            
        Returns:
            bool: Success status
        """
        try:
            product_ref = self.db.collection('products').document(product_id)
            product_ref.update({
                'quantity': new_quantity,
                'updatedAt': datetime.utcnow().isoformat() + "Z"
            })
            
            print(f"Product {product_id} quantity updated to {new_quantity}")
            return True
            
        except Exception as e:
            print(f"Error updating product quantity: {e}")
            return False
    
    # Order Management Methods (existing)
    def create_order(self, user_id: str, order_data: Dict[str, Any]) -> str:
        """
        Create a new order in Firestore
        
        Args:
            user_id: Firebase user ID from frontend
            order_data: Order information including chat message
            
        Returns:
            str: Order ID
        """
        try:
            # Prepare order document
            order_doc = {
                'user_id': user_id,
                'chat_message': order_data.get('chat_message', ''),
                'order_details': order_data.get('order_details', {}),
                'status': 'pending',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Add to Firestore
            order_ref = self.db.collection('orders').add(order_doc)
            order_id = order_ref[1].id
            
            print(f"Order created successfully with ID: {order_id}")
            return order_id
            
        except Exception as e:
            print(f"Error creating order: {e}")
            raise
    
    def get_user_orders(self, user_id: str) -> list:
        """
        Get all orders for a specific user
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            list: List of user orders
        """
        try:
            orders = []
            orders_ref = self.db.collection('orders').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
            
            for doc in orders_ref.stream():
                order_data = doc.to_dict()
                order_data['id'] = doc.id
                orders.append(order_data)
            
            return orders
            
        except Exception as e:
            print(f"Error fetching user orders: {e}")
            raise
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        Update order status
        
        Args:
            order_id: Order ID to update
            status: New status
            
        Returns:
            bool: Success status
        """
        try:
            order_ref = self.db.collection('orders').document(order_id)
            order_ref.update({
                'status': status,
                'updated_at': datetime.utcnow()
            })
            return True
            
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order by ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Optional[Dict]: Order data or None if not found
        """
        try:
            order_ref = self.db.collection('orders').document(order_id)
            order_doc = order_ref.get()
            
            if order_doc.exists:
                order_data = order_doc.to_dict()
                order_data['id'] = order_doc.id
                return order_data
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching order: {e}")
            return None

# Global Firebase client instance
firebase_client = FirebaseClient() 