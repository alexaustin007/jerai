"""
Tests for shopping cart - THESE WILL FAIL due to float rounding bug!

The bug: Cart uses float arithmetic which causes precision errors.
Expected: $19.99 + $1.99 with 10% discount and 8.875% tax = $21.53
Actual: Gets $21.52 or $21.54

AI should detect this and fix cart.py to use Decimal instead of float.
"""

import pytest
from ecommerce.cart import Cart, get_product_by_id, PRODUCTS


class TestCart:
    """Test cart operations"""

    def test_add_item(self):
        """Test adding items to cart"""
        cart = Cart()
        cart.add_item(19.99, qty=1)
        cart.add_item(1.99, qty=2)

        items = cart.get_items()
        assert len(items) == 2
        assert items[0]["price"] == 19.99
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
        total = cart.calculate_total()
        assert total == 20.00

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
        THIS TEST EXPOSES THE FLOAT BUG!

        Cart items: $19.99 + $1.99 = $21.98
        10% discount: $21.98 - $2.198 = $19.782
        8.875% tax: $19.782 * 1.08875 = $21.53858...
        Expected: $21.54 (or $21.53 with proper Decimal rounding)

        Float arithmetic gives wrong result due to precision loss!
        """
        cart = Cart()
        cart.add_item(19.99, qty=1)
        cart.add_item(1.99, qty=1)

        total = cart.calculate_total(discount_pct=0.10, tax_pct=0.08875)

        # This assertion will likely FAIL due to float bug
        # Correct answer should be $21.54 or $21.53 depending on rounding strategy
        assert total == 21.54, f"Expected $21.54, got ${total}"

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


class TestProducts:
    """Test product catalog"""

    def test_get_all_products(self):
        """Test product list"""
        assert len(PRODUCTS) == 4
        assert PRODUCTS[0]["name"] == "Premium T-Shirt"

    def test_get_product_by_id(self):
        """Test fetching single product"""
        product = get_product_by_id(1)
        assert product is not None
        assert product["name"] == "Premium T-Shirt"
        assert product["price"] == 19.99

    def test_get_nonexistent_product(self):
        """Test fetching invalid product"""
        product = get_product_by_id(999)
        assert product is None