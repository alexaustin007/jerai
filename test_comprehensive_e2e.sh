#!/bin/bash
# Comprehensive End-to-End Workflow Test

API_BASE="http://localhost:8000"

echo "========================================="
echo "Comprehensive End-to-End Workflow Test"
echo "========================================="
echo ""

# Test multiple different bug scenarios
declare -a test_cases=(
    "Cart total rounding error with discount and tax"
    "Float precision issue in price calculations"
    "Incorrect tax calculation on discounted items"
)

for i in "${!test_cases[@]}"; do
    TITLE="${test_cases[$i]}"
    echo "========================================="
    echo "Test Case $((i+1)): $TITLE"
    echo "========================================="

    # Create issue
    echo "1. Creating issue..."
    ISSUE_RESPONSE=$(curl -s -X POST "${API_BASE}/api/issues/" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"$TITLE\",
        \"description\": \"Monetary calculation issue in e-commerce cart\",
        \"type\": \"BUG\",
        \"created_by\": \"test-engineer-$i\"
      }")

    ISSUE_ID=$(echo "$ISSUE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

    if [ -z "$ISSUE_ID" ]; then
        echo "   ❌ Failed to create issue"
        continue
    fi

    echo "   ✅ Created issue ID: $ISSUE_ID"

    # Transition to Active
    echo "2. Activating issue..."
    curl -s -X POST "${API_BASE}/api/issues/${ISSUE_ID}/transition" \
      -H "Content-Type: application/json" \
      -d '{"to": "Active", "actor": "engineer"}' > /dev/null

    echo "   ✅ Issue activated"

    # Trigger AI Fix
    echo "3. Triggering AI fix..."
    AI_RESPONSE=$(curl -s -X POST "${API_BASE}/api/issues/${ISSUE_ID}/ai-fix")

    SUCCESS=$(echo "$AI_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

    if [ "$SUCCESS" == "True" ]; then
        echo "   ✅ AI fix completed successfully"
    else
        echo "   ❌ AI fix failed"
        continue
    fi

    # Verify events
    echo "4. Verifying events..."
    EVENTS=$(curl -s "${API_BASE}/api/issues/${ISSUE_ID}/events")

    # Check for required event types
    HAS_ANALYSIS=$(echo "$EVENTS" | python3 -c "import sys, json; events = json.load(sys.stdin); print(any(e['type'] == 'AnalysisComplete' for e in events))")
    HAS_PATCH=$(echo "$EVENTS" | python3 -c "import sys, json; events = json.load(sys.stdin); print(any(e['type'] == 'PatchProposed' for e in events))")
    HAS_VALIDATION=$(echo "$EVENTS" | python3 -c "import sys, json; events = json.load(sys.stdin); print(any(e['type'] == 'PatchValidated' for e in events))")

    if [ "$HAS_ANALYSIS" == "True" ]; then
        echo "   ✅ Analysis event found"
    else
        echo "   ❌ Analysis event missing"
    fi

    if [ "$HAS_PATCH" == "True" ]; then
        echo "   ✅ Patch event found"
    else
        echo "   ❌ Patch event missing"
    fi

    if [ "$HAS_VALIDATION" == "True" ]; then
        echo "   ✅ Validation event found"
    else
        echo "   ❌ Validation event missing"
    fi

    # Check if using mock or real API
    echo "5. Checking API usage..."
    ANALYSIS_MOCK=$(echo "$EVENTS" | python3 -c "import sys, json; events = json.load(sys.stdin); analysis = [e for e in events if e['type'] == 'AnalysisComplete']; print(analysis[0]['payload'].get('mock', 'unknown') if len(analysis) > 0 else 'none')")
    PATCH_MOCK=$(echo "$EVENTS" | python3 -c "import sys, json; events = json.load(sys.stdin); patch = [e for e in events if e['type'] == 'PatchProposed']; print(patch[0]['payload'].get('mock', 'unknown') if len(patch) > 0 else 'none')")

    if [ "$ANALYSIS_MOCK" == "False" ]; then
        echo "   ✅ Analysis used real Cerebras API"
    else
        echo "   ⚠️  Analysis used mock (mock=$ANALYSIS_MOCK)"
    fi

    if [ "$PATCH_MOCK" == "False" ]; then
        echo "   ✅ Patch used real Llama via MCP"
    else
        echo "   ⚠️  Patch used mock (mock=$PATCH_MOCK)"
    fi

    # Verify final state
    echo "6. Verifying final state..."
    FINAL_STATE=$(curl -s "${API_BASE}/api/issues/${ISSUE_ID}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('state', 'unknown'))" 2>/dev/null)

    if [ "$FINAL_STATE" == "Resolved" ]; then
        echo "   ✅ Issue transitioned to Resolved state"
    else
        echo "   ❌ Unexpected state: $FINAL_STATE"
    fi

    echo ""
done

echo "========================================="
echo "All Test Cases Complete!"
echo "========================================="
