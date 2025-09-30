"""
Shopping cart with INTENTIONAL FLOAT BUG for AI to fix.

The bug: Using float arithmetic causes rounding errors in tax/discount calculations.
Expected: $19.99 + $1.99 with 10% discount and 8.875% tax = $21.53
Actual: Gets $21.52 or $21.54 due to float precision issues

AI should fix by replacing float with Decimal type.
"""


class Cart:
    """Shopping cart with buggy float-based calculations"""

    def __init__(self):
        self.items = []

    def add_item(self, price: float, qty: int = 1):
        """Add item to cart"""
        self.items.append({"price": price, "qty": qty})

    def clear(self):
        """Remove all items"""
        self.items = []

    def calculate_total(self, discount_pct: float = 0.0, tax_pct: float = 0.0) -> float:
        """
        Calculate cart total with discount and tax.

        BUG: Float arithmetic causes rounding errors!
        Should use Decimal for currency calculations.

        Formula: (subtotal - discount) * (1 + tax)
        """
        # Calculate subtotal
        subtotal = sum(item["price"] * item["qty"] for item in self.items)

        # Apply discount
        discount_amount = subtotal * discount_pct
        discounted = subtotal - discount_amount

        # Apply tax
        tax_amount = discounted * tax_pct
        total = discounted + tax_amount

        # Round to 2 decimals - but float precision already lost!
        return round(total, 2)

    def get_items(self):
        """Get all cart items"""
        return self.items.copy()


# Hardcoded product catalog (no database needed for demo)
PRODUCTS = [
    {"id": 1, "name": "Premium T-Shirt", "price": 19.99, "description": "100% cotton"},
    {"id": 2, "name": "Coffee Mug", "price": 1.99, "description": "Ceramic 12oz"},
    {"id": 3, "name": "Laptop Sticker", "price": 0.99, "description": "Waterproof vinyl"},
    {"id": 4, "name": "Tech Poster", "price": 9.99, "description": "24x36 inch"},
]


def get_product_by_id(product_id: int):
    """Get product by ID"""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None