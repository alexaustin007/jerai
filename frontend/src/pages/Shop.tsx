/**
 * Minimal e-commerce shop page
 * Demonstrates the cart rounding bug that AI will fix
 */

import { useState, useEffect } from 'react';

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
}

interface CartItem {
  price: number;
  qty: number;
  name: string;
}

interface CartTotal {
  subtotal: number;
  discount_pct: number;
  tax_pct: number;
  total: number;
  items_count: number;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function Shop() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState<CartTotal | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch products on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/shop/products`)
      .then(res => res.json())
      .then(data => setProducts(data.products))
      .catch(err => console.error('Failed to load products:', err));
  }, []);

  // Add product to cart
  const addToCart = (product: Product) => {
    const existing = cart.find(item => item.name === product.name);
    if (existing) {
      setCart(cart.map(item =>
        item.name === product.name
          ? { ...item, qty: item.qty + 1 }
          : item
      ));
    } else {
      setCart([...cart, { price: product.price, qty: 1, name: product.name }]);
    }
  };

  // Calculate total with discount and tax (BUGGY!)
  const calculateTotal = async () => {
    if (cart.length === 0) {
      alert('Cart is empty!');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/shop/cart/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: cart,
          discount: 0.10,   // 10% discount
          tax: 0.08875      // 8.875% NYC tax
        })
      });

      const data = await response.json();
      setCartTotal(data);
    } catch (err) {
      console.error('Failed to calculate total:', err);
      alert('Failed to calculate total');
    } finally {
      setLoading(false);
    }
  };

  // Clear cart
  const clearCart = () => {
    setCart([]);
    setCartTotal(null);
  };

  // Calculate expected correct total for comparison
  const getExpectedTotal = () => {
    if (cart.length === 0) return 0;
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    const afterDiscount = subtotal * 0.90; // 10% off
    const withTax = afterDiscount * 1.08875; // 8.875% tax
    return withTax.toFixed(2);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h1>Demo Shop (Float Bug)</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        This shop has a rounding bug in cart calculations. Add items and calculate total to see the issue!
      </p>

      {/* Product Grid */}
      <div style={{ marginBottom: '40px' }}>
        <h2>Products</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
          {products.map(product => (
            <div key={product.id} style={{
              border: '1px solid #ddd',
              padding: '15px',
              borderRadius: '8px',
              backgroundColor: '#f9f9f9'
            }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '18px' }}>{product.name}</h3>
              <p style={{ fontSize: '14px', color: '#666', margin: '0 0 10px 0' }}>{product.description}</p>
              <p style={{ fontSize: '20px', fontWeight: 'bold', color: '#2563eb', margin: '0 0 10px 0' }}>
                ${product.price.toFixed(2)}
              </p>
              <button
                onClick={() => addToCart(product)}
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Cart */}
      <div style={{
        border: '2px solid #2563eb',
        padding: '20px',
        borderRadius: '8px',
        backgroundColor: '#f0f9ff'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2 style={{ margin: 0 }}>Shopping Cart ({cart.length} items)</h2>
          {cart.length > 0 && (
            <button
              onClick={clearCart}
              style={{
                padding: '6px 12px',
                backgroundColor: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Clear Cart
            </button>
          )}
        </div>

        {cart.length === 0 ? (
          <p style={{ color: '#666' }}>Cart is empty. Add some products!</p>
        ) : (
          <>
            <div style={{ marginBottom: '15px' }}>
              {cart.map((item, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '8px 0',
                  borderBottom: '1px solid #ddd'
                }}>
                  <span>{item.name} x {item.qty}</span>
                  <span>${(item.price * item.qty).toFixed(2)}</span>
                </div>
              ))}
            </div>

            <button
              onClick={calculateTotal}
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: loading ? '#9ca3af' : '#16a34a',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Calculating...' : 'Calculate Total (10% off + 8.875% tax)'}
            </button>

            {/* Total Display */}
            {cartTotal && (
              <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'white', borderRadius: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>Subtotal:</span>
                  <span>${cartTotal.subtotal.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#16a34a' }}>
                  <span>Discount (10%):</span>
                  <span>-${(cartTotal.subtotal * 0.10).toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>Tax (8.875%):</span>
                  <span>${(cartTotal.subtotal * 0.90 * 0.08875).toFixed(2)}</span>
                </div>
                <hr />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '20px', fontWeight: 'bold' }}>
                  <span>Total:</span>
                  <span>${cartTotal.total.toFixed(2)}</span>
                </div>

                {/* Bug Warning */}
                <div style={{
                  marginTop: '15px',
                  padding: '10px',
                  backgroundColor: '#fef3c7',
                  border: '2px solid #f59e0b',
                  borderRadius: '4px'
                }}>
                  <p style={{ margin: 0, fontWeight: 'bold', color: '#92400e' }}>
                    WARNING: Rounding Bug Detected!
                  </p>
                  <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#92400e' }}>
                    Backend uses float arithmetic. Expected total: ${getExpectedTotal()}, Got: ${cartTotal.total.toFixed(2)}
                  </p>
                  <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#92400e', fontStyle: 'italic' }}>
                    Create a bug ticket in the issue tracker and let AI fix it!
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

    </div>
  );
}