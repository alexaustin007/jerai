#!/usr/bin/env python3
"""Test MCP integration inside Docker backend container"""
import subprocess
import json

print("=" * 60)
print("Docker MCP Integration Test")
print("=" * 60)

# Test script to run inside backend container
test_script = '''
import sys
import os

# Set up environment
os.environ["WORKSPACE_PATH"] = "/workspace"
os.environ["CEREBRAS_API_KEY"] = "csk-ft2px9dhc9xffnv9eyf2frtdc8dmydxv2vhx5k9mm4ker8ex"
os.environ["CEREBRAS_API_URL"] = "https://api.cerebras.ai/v1/chat/completions"

# Import MCP client
sys.path.insert(0, "/app")
from services.mcp_client import get_mcp_client

print("\\n1. Testing MCP Client Initialization...")
try:
    mcp_client = get_mcp_client()
    print("   ✅ MCP client created successfully")
except Exception as e:
    print(f"   ❌ Failed to create MCP client: {e}")
    sys.exit(1)

print("\\n2. Testing MCP Tool Call: analyze_bug...")
try:
    result = mcp_client.call_tool(
        "analyze_bug",
        {
            "title": "Test bug - cart calculation error",
            "description": "Float rounding issue in cart total"
        }
    )

    # Check if result is valid
    if result and len(result) > 50:
        print("   ✅ analyze_bug tool returned response")
        print(f"   Response length: {len(result)} characters")
        print(f"   Preview: {result[:150]}...")

        # Check if it used real API or mock
        if "Mock" in result or "mock" in result.lower():
            print("   ⚠️  WARNING: Response might be mock")
        else:
            print("   ✅ Response appears to be real API data")
    else:
        print(f"   ❌ Invalid response: {result}")
except Exception as e:
    print(f"   ❌ Tool call failed: {e}")
    import traceback
    traceback.print_exc()

print("\\n3. Testing MCP Tool Call: generate_patch...")
try:
    result = mcp_client.call_tool(
        "generate_patch",
        {
            "title": "Fix float rounding in cart",
            "analysis": "Use Decimal for monetary calculations"
        }
    )

    if result and len(result) > 50:
        print("   ✅ generate_patch tool returned response")
        print(f"   Response length: {len(result)} characters")

        # Check for patch indicators
        if "diff" in result or "---" in result or "+++" in result:
            print("   ✅ Response contains patch diff markers")
        else:
            print("   Preview:", result[:150])
    else:
        print(f"   ❌ Invalid response: {result}")
except Exception as e:
    print(f"   ❌ Tool call failed: {e}")
    import traceback
    traceback.print_exc()
'''

print("\nRunning MCP integration test inside backend container...")
print("-" * 60)

result = subprocess.run(
    ['docker', 'exec', 'jerai-backend', 'python', '-c', test_script],
    capture_output=True,
    text=True,
    timeout=120
)

print(result.stdout)

if result.stderr:
    print("\nStderr output:")
    print(result.stderr[:500])

print("\n" + "=" * 60)
if result.returncode == 0:
    print("✅ Docker MCP Integration Test PASSED")
else:
    print("❌ Docker MCP Integration Test FAILED")
    print(f"Return code: {result.returncode}")
print("=" * 60)
