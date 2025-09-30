"""
Shop API routes for e-commerce demo.
Exposes the buggy cart calculation that AI will fix.
"""

from flask import Blueprint, jsonify, request
from ecommerce.cart import Cart, PRODUCTS, get_product_by_id

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/products', methods=['GET'])
def get_products():
    """Get all available products"""
    return jsonify({"products": PRODUCTS})


@shop_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    product = get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@shop_bp.route('/cart/calculate', methods=['POST'])
def calculate_cart():
    """
    Calculate cart total with discount and tax.

    Request body:
    {
        "items": [{"price": 19.99, "qty": 1}, ...],
        "discount": 0.10,  # 10% discount
        "tax": 0.08875     # 8.875% tax rate
    }

    This endpoint uses the BUGGY cart.py module!
    """
    try:
        data = request.json
        items = data.get('items', [])
        discount = data.get('discount', 0.0)
        tax = data.get('tax', 0.0)

        # Use buggy Cart class
        cart = Cart()
        for item in items:
            cart.add_item(price=item['price'], qty=item.get('qty', 1))

        # This calculation has the float bug!
        total = cart.calculate_total(discount_pct=discount, tax_pct=tax)

        # Calculate subtotal for display
        subtotal = sum(item['price'] * item.get('qty', 1) for item in items)

        return jsonify({
            "subtotal": round(subtotal, 2),
            "discount_pct": discount * 100,
            "tax_pct": tax * 100,
            "total": total,
            "items_count": len(items)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400