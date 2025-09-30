import { useState, useEffect } from 'react';
import './App.css';

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

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState<CartTotal | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch products
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

  // Calculate total with discount and tax (calls buggy backend!)
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
          discount: 0.10,
          tax: 0.08875
        })
      });

      const data = await response.json();
      setCartTotal(data);
    } catch (err) {
      console.error('Failed to calculate total:', err);
      alert('Failed to calculate total. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  // Clear cart
  const clearCart = () => {
    setCart([]);
    setCartTotal(null);
  };

  // Calculate expected correct total
  const getExpectedTotal = () => {
    if (cart.length === 0) return 0;
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    const afterDiscount = subtotal * 0.90;
    const withTax = afterDiscount * 1.08875;
    return withTax.toFixed(2);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>BuyNow - Online Shop</h1>
        <p>Your one-stop shop for quality products</p>
      </header>

      <main>
        {/* Products */}
        <section className="products-section">
          <h2>Featured Products</h2>
          <div className="product-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <h3>{product.name}</h3>
                <p className="description">{product.description}</p>
                <p className="price">${product.price.toFixed(2)}</p>
                <button onClick={() => addToCart(product)} className="btn-add">
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Shopping Cart */}
        <section className="cart-section">
          <div className="cart-header">
            <h2>Shopping Cart ({cart.length} items)</h2>
            {cart.length > 0 && (
              <button onClick={clearCart} className="btn-clear">
                Clear Cart
              </button>
            )}
          </div>

          {cart.length === 0 ? (
            <p className="empty-cart">Cart is empty. Start shopping!</p>
          ) : (
            <>
              <div className="cart-items">
                {cart.map((item, idx) => (
                  <div key={idx} className="cart-item">
                    <span>{item.name} x {item.qty}</span>
                    <span>${(item.price * item.qty).toFixed(2)}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={calculateTotal}
                disabled={loading}
                className="btn-calculate"
              >
                {loading ? 'Calculating...' : 'Calculate Total (10% off + 8.875% tax)'}
              </button>

              {/* Total Display */}
              {cartTotal && (
                <div className="cart-total">
                  <div className="total-row">
                    <span>Subtotal:</span>
                    <span>${cartTotal.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="total-row discount">
                    <span>Discount (10%):</span>
                    <span>-${(cartTotal.subtotal * 0.10).toFixed(2)}</span>
                  </div>
                  <div className="total-row">
                    <span>Tax (8.875%):</span>
                    <span>${(cartTotal.subtotal * 0.90 * 0.08875).toFixed(2)}</span>
                  </div>
                  <hr />
                  <div className="total-row final">
                    <span>Total:</span>
                    <span>${cartTotal.total.toFixed(2)}</span>
                  </div>

                  {/* Bug Warning */}
                  <div className="bug-warning">
                    <p className="warning-title">WARNING: Rounding Bug!</p>
                    <p className="warning-text">
                      Expected: ${getExpectedTotal()}, Got: ${cartTotal.total.toFixed(2)}
                    </p>
                    <p className="warning-hint">
                      This is a known float arithmetic bug. Report it to our dev team!
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>BuyNow Shop - Demo E-commerce Application</p>
      </footer>
    </div>
  );
}