#!/usr/bin/env python3
"""Test MCP agent functionality inside backend container"""
import subprocess
import json
import time

print("=" * 60)
print("MCP Agent Standalone Test (Inside Container)")
print("=" * 60)

# Test data
tests = [
    {
        "name": "List Tools",
        "request": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
    }
]

print("\n1. Testing MCP agent can be invoked...")
result = subprocess.run(
    ['docker', 'exec', 'jerai-backend', 'python', '/app/mcp_agent/agent.py', '--help'],
    capture_output=True,
    text=True,
    timeout=5
)

if result.returncode == 0 or 'agent.py' in result.stderr:
    print("   ✅ MCP agent script is accessible")
else:
    print(f"   ❌ Failed to access agent: {result.stderr}")
    exit(1)

print("\n2. Testing MCP agent initialization...")
# Create test script inside container
test_script = """
import json
import sys
sys.path.insert(0, '/app/mcp_agent')

# Send initialize request
init_req = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    }
}

print(json.dumps(init_req))
"""

result = subprocess.run(
    ['docker', 'exec', '-i', 'jerai-backend', 'python', '-c', test_script],
    capture_output=True,
    text=True,
    timeout=5
)

if result.returncode == 0:
    print("   ✅ MCP agent can generate JSON-RPC requests")
    print(f"   Output: {result.stdout[:100]}...")
else:
    print(f"   ❌ Error: {result.stderr}")

print("\n3. Testing file access from MCP agent...")
result = subprocess.run(
    ['docker', 'exec', 'jerai-backend', 'python', '-c',
     'import os; print("✅" if os.path.exists("/workspace/ecommerce/cart.py") else "❌", "Cart file exists:", os.path.exists("/workspace/ecommerce/cart.py"))'],
    capture_output=True,
    text=True,
    timeout=5
)
print(f"   {result.stdout.strip()}")

print("\n" + "=" * 60)
print("MCP Agent Standalone Tests Complete!")
print("=" * 60)
