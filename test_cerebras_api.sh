#!/bin/bash
# Direct Cerebras API Test

CEREBRAS_API_KEY="csk-ft2px9dhc9xffnv9eyf2frtdc8dmydxv2vhx5k9mm4ker8ex"
CEREBRAS_API_URL="https://api.cerebras.ai/v1/chat/completions"

echo "========================================="
echo "Cerebras API Direct Test"
echo "========================================="
echo ""
echo "Testing Llama 3.3 70B via Cerebras..."
echo ""

# Test 1: Simple bug analysis
curl -s -X POST "${CEREBRAS_API_URL}" \
  -H "Authorization: Bearer ${CEREBRAS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b",
    "messages": [{
      "role": "user",
      "content": "Analyze this bug: Cart total calculation shows $21.52 instead of expected $21.53 when applying 10% discount and 8.875% tax. What is the likely cause?"
    }],
    "max_tokens": 200,
    "temperature": 0.7
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'choices' in data and len(data['choices']) > 0:
        print('✅ Cerebras API Response:')
        print('Model:', data.get('model', 'unknown'))
        print('Content:', data['choices'][0]['message']['content'][:300] + '...')
        print('')
        print('✅ Token Usage:', data.get('usage', {}))
    elif 'error' in data:
        print('❌ API Error:', data['error'])
    else:
        print('❌ Unexpected response:', data)
except Exception as e:
    print('❌ Parse error:', e)
    print(sys.stdin.read())
"

echo ""
echo "========================================="
