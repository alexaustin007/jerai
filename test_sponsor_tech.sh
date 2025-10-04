#!/bin/bash
# Verify All 3 Sponsor Technologies Are Used

API_BASE="http://localhost:8000"

echo "========================================="
echo "Sponsor Technology Verification"
echo "========================================="
echo ""

# Get the latest issue (ID 14)
ISSUE_ID=14

echo "Fetching events for issue $ISSUE_ID..."
EVENTS=$(curl -s "${API_BASE}/api/issues/${ISSUE_ID}/events")

echo ""
echo "1. ✅ Cerebras API (Fast Bug Analysis)"
echo "   Model: Llama 3.3 70B"
echo "   Evidence:"

# Check Cerebras usage
ANALYSIS=$(echo "$EVENTS" | python3 -c "
import sys, json
events = json.load(sys.stdin)
analysis = [e for e in events if e['type'] == 'AnalysisComplete']
if analysis:
    payload = analysis[0]['payload']
    print(f\"   - Actor: {analysis[0]['actor']}\")
    print(f\"   - Mock: {payload.get('mock', 'unknown')}\")
    print(f\"   - Analysis length: {len(str(payload.get('analysis', '')))} chars\")
    if not payload.get('mock', True):
        print('   ✅ Real Cerebras API used')
    else:
        print('   ❌ Mock data used')
else:
    print('   ❌ No analysis found')
")
echo "$ANALYSIS"

echo ""
echo "2. ✅ Meta Llama (Code Patch Generation)"
echo "   Model: Llama 3.3 70B via Cerebras"
echo "   Evidence:"

# Check Llama/MCP usage
PATCH=$(echo "$EVENTS" | python3 -c "
import sys, json
events = json.load(sys.stdin)
patch = [e for e in events if e['type'] == 'PatchProposed']
if patch:
    payload = patch[0]['payload']
    print(f\"   - Actor: {patch[0]['actor']}\")
    print(f\"   - Mock: {payload.get('mock', 'unknown')}\")
    patch_content = str(payload.get('patch', ''))
    print(f\"   - Patch length: {len(patch_content)} chars\")

    # Check for diff markers
    if '---' in patch_content or 'diff' in patch_content:
        print('   - Contains diff markers: Yes')
    if 'Decimal' in patch_content:
        print('   - Contains Decimal fix: Yes')

    if not payload.get('mock', True):
        print('   ✅ Real Llama via MCP used')
    else:
        print('   ❌ Mock data used')
else:
    print('   ❌ No patch found')
")
echo "$PATCH"

echo ""
echo "3. ✅ Docker MCP Gateway (MCP Server Management)"
echo "   Evidence:"
echo "   - Backend logs for MCP communication:"
docker logs jerai-backend 2>&1 | grep -E "\[MCP\] Initialized successfully" | tail -3 | while read line; do
    echo "     $line"
done

echo ""
echo "   - MCP agent container check:"
if docker ps -a | grep -q "jerai-mcp-agent"; then
    echo "     ✅ MCP agent container exists"
else
    echo "     ❌ MCP agent container not found"
fi

echo ""
echo "   - Volume mounts verification:"
docker inspect jerai-backend 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data and len(data) > 0:
        mounts = data[0].get('Mounts', [])
        mcp_mount = [m for m in mounts if 'mcp_agent' in m.get('Source', '')]
        if mcp_mount:
            print('     ✅ MCP agent mounted at:', mcp_mount[0].get('Destination', 'unknown'))
        else:
            print('     ❌ MCP agent mount not found')
except:
    print('     ❌ Failed to parse container info')
"

echo ""
echo "========================================="
echo "4. Integration Summary"
echo "========================================="
echo ""

# Summary check
python3 << 'EOF'
import requests
import json

# Fetch latest issue events
response = requests.get('http://localhost:8000/api/issues/14/events')
events = response.json()

# Count sponsor tech usage
cerebras_used = False
llama_used = False
mcp_used = False

for event in events:
    if event['type'] == 'AnalysisComplete':
        if not event['payload'].get('mock', True):
            cerebras_used = True

    if event['type'] == 'PatchProposed':
        if not event['payload'].get('mock', True):
            llama_used = True
            # If patch was generated, MCP was used
            if event['actor'] == 'llama-mcp':
                mcp_used = True

print("Technology Usage Verification:")
print(f"  {'✅' if cerebras_used else '❌'} Cerebras API (Llama 3.3 70B)")
print(f"  {'✅' if llama_used else '❌'} Meta Llama (via Cerebras)")
print(f"  {'✅' if mcp_used else '❌'} Docker MCP (subprocess integration)")
print("")

if cerebras_used and llama_used and mcp_used:
    print("🎉 ALL 3 SPONSOR TECHNOLOGIES VERIFIED!")
    print("")
    print("Prize Eligibility:")
    print("  ✅ Cerebras ($5,000 + Interview)")
    print("  ✅ Meta Llama ($5,000 + Coffee Chat)")
    print("  ✅ Docker MCP ($5,000)")
    print("  💰 Total Potential: $15,000")
else:
    print("⚠️  Not all sponsor technologies verified")
EOF

echo ""
echo "========================================="
