"""
Shop API routes for e-commerce demo.
Provides clothing products and exposes the buggy cart calculation that AI will fix.
"""

from flask import Blueprint, jsonify, request

shop_bp = Blueprint('shop', __name__)

# Clothing products data (same as frontend mock data)
CLOTHING_PRODUCTS = [
    {
        "id": 1,
        "name": "Classic Cotton Shirt",
        "price": 29.99,
        "description": "100% organic cotton, available in multiple colors",
        "category": "shirts",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop"
    },
    {
        "id": 2,
        "name": "Denim Casual Shirt",
        "price": 39.99,
        "description": "Premium denim with comfortable fit",
        "category": "shirts",
        "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop"
    },
    {
        "id": 3,
        "name": "Business Dress Shirt",
        "price": 49.99,
        "description": "Professional dress shirt for office wear",
        "category": "shirts",
        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=300&h=300&fit=crop"
    },
    {
        "id": 4,
        "name": "Leather Work Boots",
        "price": 89.99,
        "description": "Durable leather boots for all-day comfort",
        "category": "boots",
        "image": "https://images.unsplash.com/photo-1553699357-b454793abefa?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "id": 5,
        "name": "Hiking Boots",
        "price": 79.99,
        "description": "Waterproof hiking boots with ankle support",
        "category": "boots",
        "image": "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=300&h=300&fit=crop"
    },
    {
        "id": 6,
        "name": "Chelsea Boots",
        "price": 99.99,
        "description": "Stylish Chelsea boots for casual and formal wear",
        "category": "boots",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop"
    },
    {
        "id": 7,
        "name": "Wool Socks",
        "price": 12.99,
        "description": "Merino wool socks, pack of 3",
        "category": "socks",
        "image": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=300&h=300&fit=crop"
    },
    {
        "id": 8,
        "name": "Athletic Socks",
        "price": 8.99,
        "description": "Moisture-wicking athletic socks, pack of 5",
        "category": "socks",
        "image": "https://images.unsplash.com/photo-1733409896722-56913a549739?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YmxhY2slMjBzb2Nrc3xlbnwwfHwwfHx8MA%3D%3D"
    },
    {
        "id": 9,
        "name": "Dress Socks",
        "price": 15.99,
        "description": "Premium dress socks for business attire",
        "category": "socks",
        "image": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=300&h=300&fit=crop"
    },
    {
        "id": 10,
        "name": "Designer Jeans",
        "price": 59.99,
        "description": "Premium denim jeans with perfect fit",
        "category": "clothes",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop"
    },
    {
        "id": 11,
        "name": "Cozy Sweater",
        "price": 49.99,
        "description": "Soft knit sweater for cold weather",
        "category": "clothes",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop"
    },
    {
        "id": 12,
        "name": "Leather Jacket",
        "price": 149.99,
        "description": "Genuine leather jacket with classic styling",
        "category": "clothes",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop"
    }
]


def simulate_buggy_cart_calculation(items, discount_pct=0.0, tax_pct=0.0):
    """
    BUGGY CART CALCULATION - Same logic as frontend mock
    
    This simulates the same float precision bug that causes rounding errors!
    The bug: Using float arithmetic causes precision issues in money calculations.
    """
    # Calculate subtotal (items should be in regular dollars, not cents)
    subtotal = sum(item['price'] * item.get('qty', 1) for item in items)
    
    # Apply discount (float arithmetic causes precision issues)
    discount_amount = subtotal * discount_pct
    after_discount = subtotal - discount_amount
    
    # Apply tax (more float arithmetic)
    tax_amount = after_discount * tax_pct
    total = after_discount + tax_amount
    
    # This is where the rounding bug occurs - float precision is already lost!
    return {
        "subtotal": subtotal,
        "discount_pct": discount_pct,
        "tax_pct": tax_pct,
        "total": round(total, 2),  # Buggy rounding due to float precision
        "items_count": sum(item.get('qty', 1) for item in items)
    }


@shop_bp.route('/products', methods=['GET'])
def get_products():
    """Get all available clothing products"""
    return jsonify({"products": CLOTHING_PRODUCTS})


@shop_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    product = next((p for p in CLOTHING_PRODUCTS if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@shop_bp.route('/cart/calculate', methods=['POST'])
def calculate_cart():
    """
    Calculate cart total with discount and tax - CONTAINS INTENTIONAL BUG!

    Request body:
    {
        "items": [{"price": 29.99, "qty": 1}, ...],  # prices in dollars
        "discount": 0.10,  # 10% discount
        "tax": 0.08875     # 8.875% tax rate
    }

    This endpoint uses BUGGY float arithmetic that causes rounding errors!
    """
    try:
        data = request.json
        items = data.get('items', [])
        discount = data.get('discount', 0.0)
        tax = data.get('tax', 0.0)

        if not items:
            return jsonify({"error": "No items in cart"}), 400

        # Use the buggy calculation function
        result = simulate_buggy_cart_calculation(items, discount, tax)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400