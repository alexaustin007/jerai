#!/bin/bash
# Test MCP Integration End-to-End

API_BASE="http://localhost:8000"

echo "========================================="
echo "MCP Integration Test"
echo "========================================="

# Test 1: Create an issue
echo ""
echo "1. Creating test issue..."
ISSUE_RESPONSE=$(curl -s -X POST "${API_BASE}/api/issues/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cart total calculation bug - float rounding error",
    "description": "When applying 10% discount and 8.875% tax to cart total, getting $21.52 instead of expected $21.53",
    "type": "BUG",
    "created_by": "test-user"
  }')

echo "$ISSUE_RESPONSE" | python3 -m json.tool
ISSUE_ID=$(echo "$ISSUE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "   Created issue ID: $ISSUE_ID"

# Test 2: Transition to Active
echo ""
echo "2. Transitioning issue to ACTIVE..."
curl -s -X POST "${API_BASE}/api/issues/${ISSUE_ID}/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "Active",
    "actor": "engineer"
  }' | python3 -m json.tool

# Test 3: Trigger AI Fix (this will test MCP subprocess)
echo ""
echo "3. Triggering AI Fix (MCP subprocess test)..."
AI_FIX_RESPONSE=$(curl -s -X POST "${API_BASE}/api/issues/${ISSUE_ID}/ai-fix" \
  -H "Content-Type: application/json")

echo "$AI_FIX_RESPONSE" | python3 -m json.tool

# Test 4: Get events to see MCP results
echo ""
echo "4. Fetching events (should show MCP analysis and patch)..."
curl -s "${API_BASE}/api/issues/${ISSUE_ID}/events" | python3 -m json.tool

echo ""
echo "========================================="
echo "Test Complete!"
echo "========================================="
