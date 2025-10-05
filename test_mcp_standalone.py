#!/usr/bin/env python3
"""Standalone test for MCP agent"""
import subprocess
import json
import os

# Set up environment
env = os.environ.copy()
env['WORKSPACE_PATH'] = os.path.join(os.getcwd(), 'backend')
env['CEREBRAS_API_KEY'] = env.get('CEREBRAS_API_KEY', 'test-key')
env['CEREBRAS_API_URL'] = 'https://api.cerebras.ai/v1/chat/completions'

print("Testing MCP Agent Standalone")
print("=" * 60)

# Test 1: List tools
print("\n1. Testing list_tools...")
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}

try:
    process = subprocess.Popen(
        ['python3', 'mcp_agent/agent.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )

    stdout, stderr = process.communicate(
        input=json.dumps(request) + "\n",
        timeout=10
    )

    print(f"   Exit code: {process.returncode}")

    if stderr:
        print(f"   Stderr: {stderr[:200]}")

    # Parse response
    for line in stdout.split('\n'):
        if line.strip().startswith('{'):
            try:
                response = json.loads(line)
                if 'result' in response:
                    print(f"   ✓ Success: Found {len(response['result'])} tools")
                    for tool in response['result']:
                        print(f"      - {tool.get('name', 'unknown')}")
                elif 'error' in response:
                    print(f"   ✗ Error: {response['error']}")
            except json.JSONDecodeError as e:
                print(f"   ✗ JSON decode error: {e}")

except subprocess.TimeoutExpired:
    process.kill()
    print("   ✗ Timeout")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n" + "=" * 60)
