# Jerai - AI-Powered Bug Tracker with Clothing E-commerce Demo

A hackathon project that demonstrates AI-assisted bug fixing using three sponsor technologies:
- **Cerebras API**: Ultra-fast bug analysis with Llama 3.3 70B
- **Meta Llama 3.3 70B**: AI model for code analysis and patch generation  
- **Docker MCP Gateway**: Containerized agent with safe filesystem access

## 🎯 Project Overview

Jerai is a minimal Jira-like issue tracker that automatically fixes bugs using AI. The demo includes a clothing e-commerce website with an **intentional cart calculation bug** that demonstrates float arithmetic precision issues.

### Demo Flow
1. **Create bug** → Issue appears in "New" column
2. **Activate issue** → Moves to "Active" column  
3. **Click "AI Fix"** → AI analyzes and generates patch
4. **Auto-resolve** → Issue moves to "Resolved" → "Closed"
5. **View patch** → Complete diff shown in event trail

## 🛍️ Clothing E-commerce Demo

The e-commerce app (`/ecommerce-app/`) showcases a clothing store with:

- **Product Categories**: Shirts, Boots, Socks, General Clothes
- **Product Images**: High-quality clothing photos from Unsplash
- **Intentional Bug**: Cart calculation uses float arithmetic causing rounding errors

### Bug Example
```
Items: Classic Cotton Shirt ($29.99) + Wool Socks ($12.99) = $42.98
With 10% discount and 8.875% tax:
- Expected: $42.11 (correct decimal math)
- Actual: $42.10 or $42.12 (float precision error)
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Cerebras API key (get free tier at [cerebras.ai](https://cerebras.ai))

### Setup
```bash
# 1. Clone and setup environment
git clone <repo-url>
cd jerai
cp .env.example .env

# 2. Add your Cerebras API key to .env
echo "CEREBRAS_API_KEY=your_key_here" >> .env

# 3. Start all services
docker compose up --build

# 4. Access applications
# - Main Jerai Tracker: http://localhost:5173
# - Clothing E-commerce: http://localhost:5174  
# - Backend API: http://localhost:8000
```

## 🏗️ Architecture

```
Frontend (React)     E-commerce App (React)
     ↓                        ↓
Backend (Flask) ←→ MySQL Database
     ↓
Cerebras API (Analysis) → Docker MCP Gateway → MCP Agent (Patches)
```

### Key Components

- **Frontend**: React + TypeScript Kanban board for issue tracking
- **E-commerce App**: Separate React app demonstrating the cart bug
- **Backend**: Flask REST API with state machine enforcement
- **Database**: MySQL with 2 tables (issues + events)
- **AI Services**: Integrated Cerebras + Llama + Docker MCP

## 📁 Project Structure

```
jerai/
├── frontend/                # Main issue tracker UI
├── ecommerce-app/          # Clothing store demo (port 5174)
├── backend/                # Flask API
│   ├── ecommerce/cart.py   # 🐛 BUGGY cart calculation
│   ├── routes/shop.py      # E-commerce API endpoints
│   └── tests/test_cart.py  # Tests that expose the bug
├── mcp_agent/              # Containerized AI agent
├── db/init/                # Database schema + demo data
└── docker-compose.yml      # All services
```

## 🧪 Testing the Bug

### Run Tests (Will Fail Due to Bug)
```bash
cd backend
python3 -m pytest tests/test_cart.py -v
```

### Manual Testing
```bash
cd backend
python3 -c "
from ecommerce.cart import compute_total
items = [{'price': 1999, 'qty': 1}, {'price': 199, 'qty': 1}]
total = compute_total(items, discount_pct=0.10, tax_pct=0.08875)
print(f'Expected: 2153 cents, Got: {total} cents, Bug: {total != 2153}')
"
```

## 🛒 Using the Clothing Store

1. **Visit**: http://localhost:5174
2. **Browse**: Clothing products with images and categories
3. **Add to Cart**: Select shirts, boots, socks, etc.
4. **Calculate Total**: Click "Calculate Total" button
5. **See Bug**: Warning box shows expected vs actual totals

### Product Categories
- **Shirts**: Classic Cotton Shirt, Denim Casual Shirt
- **Boots**: Leather Work Boots, Hiking Boots  
- **Socks**: Wool Socks, Athletic Socks
- **Clothes**: Designer Jeans, Cozy Sweater

## 🤖 AI Fix Workflow

1. **Cerebras Analysis** (< 3 seconds): Fast bug analysis using Llama 3.3 70B
2. **MCP Gateway**: Routes request to containerized agent
3. **Llama Patch Generation**: Creates fix using Decimal instead of float
4. **Test Validation**: Runs tests to verify fix works
5. **Auto-Resolution**: Issue automatically moves to resolved state

## 🎯 Expected AI Fix

The AI should detect and fix the float arithmetic bug by:

```python
# BEFORE (buggy)
subtotal = sum(item['price'] * item.get('qty', 1) for item in items) / 100.0
total = after_discount + tax
return round(total * 100)

# AFTER (fixed)  
from decimal import Decimal, ROUND_HALF_UP
subtotal = sum(item['price'] * item.get('qty', 1) for item in items)  # keep as cents
discount = int(Decimal(subtotal) * Decimal(str(discount_pct)))
# ... proper Decimal arithmetic throughout
```

## 📊 Database Schema

### Issues Table
- `id`, `title`, `type`, `state`, `created_by`, `timestamps`
- States: New → Active → Resolved → Closed

### Events Table (Audit Trail)
- `id`, `issue_id`, `type`, `actor`, `payload_json`, `ts`
- All AI outputs stored in `payload_json` field

## 🏆 Sponsor Technology Integration

### ✅ Cerebras API ($5,000 Prize)
- **File**: `backend/services/ai_service.py`
- **Usage**: Fast bug analysis with Llama 3.3 70B
- **Endpoint**: `https://api.cerebras.ai/v1/chat/completions`

### ✅ Meta Llama 3.3 70B ($5,000 Prize)  
- **Model**: `llama-3.3-70b` via Cerebras infrastructure
- **Usage**: Code analysis and patch generation
- **Integration**: All AI requests specify Llama model

### ✅ Docker MCP Gateway ($5,000 Prize)
- **Service**: `mcp-gateway` in docker-compose.yml
- **Usage**: Containerized agent with safe filesystem access
- **Routing**: Backend → Gateway → MCP Agent

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python3 app.py  # Runs on :8000
```

### Frontend Development  
```bash
cd frontend
npm install && npm run dev  # Runs on :5173
```

### E-commerce App Development
```bash
cd ecommerce-app  
npm install && npm run dev  # Runs on :5174
```

## 🎥 Demo Script (2 minutes)

1. **Show clothing store** (30s): Browse products, add to cart, see bug warning
2. **Create issue** (15s): Report the cart bug in main tracker
3. **Activate & AI Fix** (60s): Watch AI analyze → generate patch → resolve
4. **Show results** (15s): View event trail with complete patch diff

## 🏁 Success Criteria

- ✅ Clothing e-commerce with intentional cart bug
- ✅ Tests that demonstrate the float precision issue
- ✅ All 3 sponsor technologies integrated
- ✅ Complete AI workflow (analysis → patch → validation)
- ✅ Beautiful UI with product images
- ✅ Single command setup (`docker compose up`)

---

**Total Prize Potential**: $15,000 (all 3 sponsors)  
**Demo Time**: < 2 minutes end-to-end  
**Bug Complexity**: Real float arithmetic precision issue  
**AI Challenge**: Detect pattern, understand context, generate proper Decimal-based fix