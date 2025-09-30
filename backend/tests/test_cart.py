"""
Tests for clothing cart - THESE WILL FAIL due to float rounding bug!

The bug: Cart uses float arithmetic which causes precision errors.
Expected: Classic Cotton Shirt ($29.99) + Wool Socks ($12.99) = $42.98
With 10% discount and 8.875% tax should be $41.63
Actual: Gets wrong result due to float precision

AI should detect this and fix cart.py to use Decimal instead of float.
"""

import pytest
from ecommerce.cart import Cart, get_product_by_id, CLOTHING_PRODUCTS, compute_total


class TestCart:
    """Test cart operations"""

    def test_add_item(self):
        """Test adding clothing items to cart"""
        cart = Cart()
        cart.add_item(29.99, qty=1)  # Classic Cotton Shirt
        cart.add_item(12.99, qty=2)  # 2x Wool Socks

        items = cart.get_items()
        assert len(items) == 2
        assert items[0]["price"] == 2999  # Stored as cents
        assert items[1]["qty"] == 2

    def test_clear_cart(self):
        """Test clearing cart"""
        cart = Cart()
        cart.add_item(10.00, qty=1)
        cart.clear()
        assert len(cart.get_items()) == 0

    def test_simple_total_no_tax_discount(self):
        """Test basic total calculation"""
        cart = Cart()
        cart.add_item(10.00, qty=2)
        result = cart.calculate_total()
        assert result["total"] == 20.00
        assert result["subtotal"] == 20.00

    def test_total_with_discount(self):
        """Test total with 10% discount"""
        cart = Cart()
        cart.add_item(100.00, qty=1)
        total = cart.calculate_total(discount_pct=0.10)
        assert total == 90.00

    def test_total_with_tax(self):
        """Test total with 8.875% tax"""
        cart = Cart()
        cart.add_item(100.00, qty=1)
        total = cart.calculate_total(tax_pct=0.08875)
        assert total == 108.88  # May fail due to rounding

    def test_buggy_calculation_discount_then_tax(self):
        """
        THIS TEST EXPOSES THE FLOAT BUG with clothing items!

        Cart items: Classic Cotton Shirt ($29.99) + Wool Socks ($12.99) = $42.98
        10% discount: $42.98 - $4.298 = $38.682
        8.875% tax: $38.682 * 1.08875 = $42.115...
        Expected: $42.11 or $42.12 (depending on rounding strategy)

        Float arithmetic gives wrong result due to precision loss!
        """
        cart = Cart()
        cart.add_item(29.99, qty=1)  # Classic Cotton Shirt
        cart.add_item(12.99, qty=1)  # Wool Socks

        result = cart.calculate_total(discount_pct=0.10, tax_pct=0.08875)
        total = result["total"]

        # This assertion will likely FAIL due to float bug
        # Correct answer should be around $42.11-42.12
        expected = 42.11
        assert abs(total - expected) < 0.02, f"Expected ~${expected:.2f}, got ${total:.2f} (difference: ${abs(total-expected):.4f})"

    def test_multiple_quantities(self):
        """Test with multiple quantities"""
        cart = Cart()
        cart.add_item(5.00, qty=3)
        cart.add_item(2.00, qty=2)

        # Subtotal: 15 + 4 = 19
        # 5% discount: 19 - 0.95 = 18.05
        # 10% tax: 18.05 * 1.10 = 19.855 ≈ 19.86
        total = cart.calculate_total(discount_pct=0.05, tax_pct=0.10)
        assert abs(total - 19.86) < 0.01  # Allow small tolerance


class TestClothingProducts:
    """Test clothing product catalog"""

    def test_get_all_products(self):
        """Test clothing product list"""
        assert len(CLOTHING_PRODUCTS) >= 6
        assert CLOTHING_PRODUCTS[0]["name"] == "Classic Cotton Shirt"
        assert CLOTHING_PRODUCTS[0]["category"] == "shirts"

    def test_get_product_by_id(self):
        """Test fetching single clothing product"""
        product = get_product_by_id(1)
        assert product is not None
        assert product["name"] == "Classic Cotton Shirt"
        assert product["price"] == 29.99
        assert "image" in product
        assert "category" in product

    def test_get_nonexistent_product(self):
        """Test fetching invalid product"""
        product = get_product_by_id(999)
        assert product is None

    def test_product_categories(self):
        """Test that we have products in different clothing categories"""
        categories = set(product["category"] for product in CLOTHING_PRODUCTS)
        expected_categories = {"shirts", "boots", "socks", "clothes"}
        assert categories.intersection(expected_categories), f"Expected clothing categories, got {categories}"


class TestComputeTotal:
    """Test the buggy compute_total function directly"""

    def test_compute_total_clothing_bug(self):
        """
        Test the compute_total function with clothing prices - this should demonstrate the bug!
        
        This is the core function that contains the float arithmetic bug.
        """
        items = [
            {"price": 2999, "qty": 1},  # Classic Cotton Shirt $29.99 in cents
            {"price": 1299, "qty": 1}   # Wool Socks $12.99 in cents  
        ]
        
        total_cents = compute_total(items, discount_pct=0.10, tax_pct=0.08875)
        
        # Manual calculation (what it SHOULD be):
        # Subtotal: 2999 + 1299 = 4298 cents ($42.98)
        # Convert to dollars: $42.98
        # Discount 10%: $42.98 * 0.90 = $38.682
        # Tax 8.875%: $38.682 * 1.08875 = $42.115...
        # Back to cents: 4211 or 4212 cents
        
        expected_cents = 4211  # $42.11
        
        print(f"Expected: {expected_cents} cents (${expected_cents/100:.2f})")
        print(f"Actual: {total_cents} cents (${total_cents/100:.2f})")
        print(f"Difference: {abs(total_cents - expected_cents)} cents")
        
        # This assertion might FAIL due to the float bug - that's the point!
        assert abs(total_cents - expected_cents) <= 2, f"Float bug detected! Expected ~{expected_cents} cents, got {total_cents} cents"