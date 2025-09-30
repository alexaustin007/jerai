"""
Shopping cart with INTENTIONAL FLOAT BUG for AI to fix.

The bug: Using float arithmetic causes rounding errors in tax/discount calculations.
Expected: Classic Cotton Shirt ($29.99) + Wool Socks ($12.99) = $42.98
With 10% discount and 8.875% tax should be $41.63
Actual: Gets $41.62 or $41.64 due to float precision issues

AI should fix by replacing float with Decimal type.
"""


def compute_total(items, discount_pct=0.0, tax_pct=0.0):
    """
    Compute cart total with discount and tax - BUGGY VERSION
    
    BUG: Using float causes rounding errors in money calculations
    Example: 29.99 + 12.99 = 42.98 with 10% discount and 8.875% tax
    Should be $41.63, but float math gives $41.62 or $41.64
    
    Formula: (subtotal - discount) * (1 + tax_rate)
    """
    # Convert cents to dollars (this introduces float precision issues)
    subtotal = sum(item['price'] * item.get('qty', 1) for item in items) / 100.0
    
    # Apply discount (float arithmetic)
    discount = subtotal * discount_pct
    after_discount = subtotal - discount
    
    # Apply tax (more float arithmetic)
    tax = after_discount * tax_pct
    total = after_discount + tax
    
    # Convert back to cents, but rounding is wrong due to float precision!
    return round(total * 100)


class Cart:
    """Shopping cart with buggy float-based calculations"""

    def __init__(self):
        self.items = []

    def add_item(self, price: float, qty: int = 1):
        """Add item to cart (price in cents)"""
        self.items.append({"price": int(price * 100), "qty": qty})

    def clear(self):
        """Remove all items"""
        self.items = []

    def calculate_total(self, discount_pct: float = 0.0, tax_pct: float = 0.0) -> dict:
        """
        Calculate cart total with discount and tax using buggy function.
        Returns dict with breakdown for frontend display.
        """
        if not self.items:
            return {"subtotal": 0, "total": 0, "items_count": 0}
            
        # Use the buggy compute_total function
        total_cents = compute_total(self.items, discount_pct, tax_pct)
        subtotal_cents = sum(item["price"] * item["qty"] for item in self.items)
        
        return {
            "subtotal": subtotal_cents / 100.0,
            "discount_pct": discount_pct,
            "tax_pct": tax_pct,
            "total": total_cents / 100.0,
            "items_count": sum(item["qty"] for item in self.items)
        }

    def get_items(self):
        """Get all cart items"""
        return self.items.copy()


# Clothing product catalog with realistic prices
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
        "name": "Leather Work Boots",
        "price": 89.99,
        "description": "Durable leather boots for all-day comfort",
        "category": "boots",
        "image": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=300&h=300&fit=crop"
    },
    {
        "id": 4,
        "name": "Hiking Boots",
        "price": 79.99,
        "description": "Waterproof hiking boots with ankle support",
        "category": "boots",
        "image": "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=300&h=300&fit=crop"
    },
    {
        "id": 5,
        "name": "Wool Socks",
        "price": 12.99,
        "description": "Merino wool socks, pack of 3",
        "category": "socks",
        "image": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=300&h=300&fit=crop"
    },
    {
        "id": 6,
        "name": "Athletic Socks",
        "price": 8.99,
        "description": "Moisture-wicking athletic socks, pack of 5",
        "category": "socks",
        "image": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=300&h=300&fit=crop"
    },
    {
        "id": 7,
        "name": "Designer Jeans",
        "price": 59.99,
        "description": "Premium denim jeans with perfect fit",
        "category": "clothes",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop"
    },
    {
        "id": 8,
        "name": "Cozy Sweater",
        "price": 49.99,
        "description": "Soft knit sweater for cold weather",
        "category": "clothes",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop"
    }
]


def get_product_by_id(product_id: int):
    """Get product by ID"""
    for product in CLOTHING_PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def get_all_products():
    """Get all products"""
    return CLOTHING_PRODUCTS