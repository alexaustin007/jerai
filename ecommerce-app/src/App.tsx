import { useState, useEffect } from 'react';
import './App.css';

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  category: string;
  image: string;
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

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState<CartTotal | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('all');

  // Initialize products from backend API
  useEffect(() => {
    fetch(`${API_BASE}/api/shop/products`)
      .then(res => res.json())
      .then(data => {
        console.log('✅ Loaded products from backend:', data.products.length);
        setProducts(data.products);
        setFilteredProducts(data.products);
      })
      .catch(err => {
        console.error('❌ Failed to load products from backend:', err);
        // You could add fallback mock data here if needed
        setProducts([]);
        setFilteredProducts([]);
      });
  }, []);

  // Category filter functionality
  const filterProducts = (category: string) => {
    setActiveFilter(category);
    if (category === 'all') {
      setFilteredProducts(products);
    } else {
      setFilteredProducts(products.filter(product => product.category === category));
    }
  };

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

  // Remove item from cart
  const removeFromCart = (productName: string) => {
    setCart(cart.filter(item => item.name !== productName));
  };

  // Update item quantity
  const updateQuantity = (productName: string, newQty: number) => {
    if (newQty <= 0) {
      removeFromCart(productName);
      return;
    }
    setCart(cart.map(item =>
      item.name === productName
        ? { ...item, qty: newQty }
        : item
    ));
  };

  // Calculate total with discount and tax (backend API call)
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

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Cart calculation from backend:', data);
        setCartTotal(data);
      } else {
        throw new Error(`Backend error: ${response.status}`);
      }
    } catch (err) {
      console.error('❌ Failed to calculate total from backend:', err);
      
      // Fallback to local calculation if backend is down
      const subtotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
      const discountAmount = subtotal * 0.10;
      const afterDiscount = subtotal - discountAmount;
      const taxAmount = afterDiscount * 0.08875;
      const total = afterDiscount + taxAmount;
      
      const fallbackResult = {
        subtotal: subtotal,
        discount_pct: 0.10,
        tax_pct: 0.08875,
        total: Math.round(total * 100) / 100,
        items_count: cart.reduce((sum, item) => sum + item.qty, 0)
      };
      
      setCartTotal(fallbackResult);
      alert('Backend unavailable, using fallback calculation');
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
        <h1>ClothingCo - Fashion Store</h1>
        <p>Premium clothing for every occasion</p>
      </header>

      <main>
        {/* Products */}
        <section className="products-section">
          <h2>Featured Clothing</h2>
          
          {/* Category Filter */}
          <div className="category-filters">
            <button 
              className={`filter-btn ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => filterProducts('all')}
            >
              All ({products.length})
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'shirts' ? 'active' : ''}`}
              onClick={() => filterProducts('shirts')}
            >
              Shirts ({products.filter(p => p.category === 'shirts').length})
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'boots' ? 'active' : ''}`}
              onClick={() => filterProducts('boots')}
            >
              Boots ({products.filter(p => p.category === 'boots').length})
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'socks' ? 'active' : ''}`}
              onClick={() => filterProducts('socks')}
            >
              Socks ({products.filter(p => p.category === 'socks').length})
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'clothes' ? 'active' : ''}`}
              onClick={() => filterProducts('clothes')}
            >
              Clothes ({products.filter(p => p.category === 'clothes').length})
            </button>
          </div>

          <div className="product-grid">
            {filteredProducts.map(product => (
              <div key={product.id} className="product-card">
                <div className="product-image">
                  <img src={product.image} alt={product.name} />
                  <div className="category-badge">{product.category}</div>
                </div>
                <div className="product-info">
                  <h3>{product.name}</h3>
                  <p className="description">{product.description}</p>
                  <p className="price">${product.price.toFixed(2)}</p>
                  <button 
                    onClick={() => addToCart(product)} 
                    className="btn-add"
                    disabled={cart.some(item => item.name === product.name)}
                  >
                    {cart.some(item => item.name === product.name) ? '✓ In Cart' : 'Add to Cart'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Shopping Cart */}
        <section className="cart-section">
          <div className="cart-header">
            <h2>Shopping Cart ({cart.reduce((sum, item) => sum + item.qty, 0)} items)</h2>
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
                    <div className="item-info">
                      <span className="item-name">{item.name}</span>
                      <span className="item-price">${item.price.toFixed(2)} each</span>
                    </div>
                    <div className="item-controls">
                      <div className="quantity-controls">
                        <button 
                          className="qty-btn"
                          onClick={() => updateQuantity(item.name, item.qty - 1)}
                        >
                          -
                        </button>
                        <span className="quantity">{item.qty}</span>
                        <button 
                          className="qty-btn"
                          onClick={() => updateQuantity(item.name, item.qty + 1)}
                        >
                          +
                        </button>
                      </div>
                      <span className="item-total">${(item.price * item.qty).toFixed(2)}</span>
                      <button 
                        className="remove-btn"
                        onClick={() => removeFromCart(item.name)}
                        title="Remove item"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={calculateTotal}
                disabled={loading}
                className="btn-calculate"
              >
                {loading ? 'Calculating...' : '🧮 Calculate Total (10% off + 8.875% tax)'}
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
                    <span>${((cartTotal.subtotal * 0.90) * 0.08875).toFixed(2)}</span>
                  </div>
                  <hr />
                  <div className="total-row final">
                    <span>Total:</span>
                    <span>${cartTotal.total.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>ClothingCo - Demo E-commerce with Intentional Cart Bug</p>
      </footer>
    </div>
  );
}