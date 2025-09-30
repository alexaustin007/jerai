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

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState<CartTotal | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('all');

  // Mock clothing products data (UI-only, no backend needed)
  const mockProducts: Product[] = [
    {
      id: 1,
      name: "Classic Cotton Shirt",
      price: 29.99,
      description: "100% organic cotton, available in multiple colors",
      category: "shirts",
      image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop"
    },
    {
      id: 2,
      name: "Denim Casual Shirt",
      price: 39.99,
      description: "Premium denim with comfortable fit",
      category: "shirts",
      image: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop"
    },
    {
      id: 3,
      name: "Business Dress Shirt",
      price: 49.99,
      description: "Professional dress shirt for office wear",
      category: "shirts",
      image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=300&h=300&fit=crop"
    },
    {
      id: 4,
      name: "Leather Work Boots",
      price: 89.99,
      description: "Durable leather boots for all-day comfort",
      category: "boots",
      image: "https://images.unsplash.com/photo-1553699357-b454793abefa?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
      id: 5,
      name: "Hiking Boots",
      price: 79.99,
      description: "Waterproof hiking boots with ankle support",
      category: "boots",
      image: "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=300&h=300&fit=crop"
    },
    {
      id: 6,
      name: "Chelsea Boots",
      price: 99.99,
      description: "Stylish Chelsea boots for casual and formal wear",
      category: "boots",
      image: "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop"
    },
    {
      id: 7,
      name: "Wool Socks",
      price: 12.99,
      description: "Merino wool socks, pack of 3",
      category: "socks",
      image: "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=300&h=300&fit=crop"
    },
    {
      id: 8,
      name: "Athletic Socks",
      price: 8.99,
      description: "Moisture-wicking athletic socks, pack of 5",
      category: "socks",
      image: "https://images.unsplash.com/photo-1733409896722-56913a549739?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YmxhY2slMjBzb2Nrc3xlbnwwfHwwfHx8MA%3D%3D"
    },
    {
      id: 9,
      name: "Dress Socks",
      price: 15.99,
      description: "Premium dress socks for business attire",
      category: "socks",
      image: "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=300&h=300&fit=crop"
    },
    {
      id: 10,
      name: "Designer Jeans",
      price: 59.99,
      description: "Premium denim jeans with perfect fit",
      category: "clothes",
      image: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop"
    },
    {
      id: 11,
      name: "Cozy Sweater",
      price: 49.99,
      description: "Soft knit sweater for cold weather",
      category: "clothes",
      image: "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop"
    },
    {
      id: 12,
      name: "Leather Jacket",
      price: 149.99,
      description: "Genuine leather jacket with classic styling",
      category: "clothes",
      image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop"
    }
  ];

  // Initialize products on component mount
  useEffect(() => {
    setProducts(mockProducts);
    setFilteredProducts(mockProducts);
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

  // Simulate the buggy cart calculation (frontend-only)
  const simulateBuggyCalculation = (items: CartItem[], discount: number, tax: number) => {
    // This simulates the same float precision bug that would be in the backend!
    const subtotal = items.reduce((sum, item) => sum + item.price * item.qty, 0);
    
    // Apply discount (float arithmetic causes precision issues)
    const discountAmount = subtotal * discount;
    const afterDiscount = subtotal - discountAmount;
    
    // Apply tax (more float arithmetic)
    const taxAmount = afterDiscount * tax;
    const total = afterDiscount + taxAmount;
    
    // This is where the rounding bug occurs - float precision is already lost!
    return {
      subtotal: subtotal,
      discount_pct: discount,
      tax_pct: tax,
      total: Math.round(total * 100) / 100, // Buggy rounding due to float precision
      items_count: items.reduce((sum, item) => sum + item.qty, 0)
    };
  };

  // Calculate total with discount and tax (frontend simulation)
  const calculateTotal = () => {
    if (cart.length === 0) {
      alert('Cart is empty!');
      return;
    }

    setLoading(true);
    
    // Simulate loading delay for realistic UX
    setTimeout(() => {
      const result = simulateBuggyCalculation(cart, 0.10, 0.08875);
      setCartTotal(result);
      setLoading(false);
    }, 800);
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

                  {/* Bug Warning */}
                  <div className="bug-warning">
                    <p className="warning-title">⚠️ ROUNDING BUG DETECTED!</p>
                    <p className="warning-text">
                      <strong>Expected (correct math):</strong> ${getExpectedTotal()}
                    </p>
                    <p className="warning-text">
                      <strong>Actual (buggy float):</strong> ${cartTotal.total.toFixed(2)}
                    </p>
                    <p className="warning-text">
                      <strong>Difference:</strong> ${Math.abs(parseFloat(getExpectedTotal()) - cartTotal.total).toFixed(2)}
                    </p>
                    <p className="warning-hint">
                      🐛 This is a float arithmetic precision bug! The AI system should detect and fix this using Decimal arithmetic.
                    </p>
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