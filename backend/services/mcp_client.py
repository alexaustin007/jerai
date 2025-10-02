import os
import subprocess
import json
from typing import Dict, Any

class MCPClient:
    """Client for communicating with MCP server via stdio"""
    
    def __init__(self, server_command: str, server_args: list = None, env: dict = None):
        self.server_command = server_command
        self.server_args = server_args or []
        self.env = {**os.environ, **(env or {})}
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool and return the result"""

        # Start MCP server process
        cmd = [self.server_command] + self.server_args

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.env,
                text=True,
                bufsize=0
            )

            # Step 1: Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "jerai-backend",
                        "version": "1.0.0"
                    }
                }
            }

            try:
                process.stdin.write(json.dumps(init_request) + "\n")
                process.stdin.flush()
            except Exception as e:
                raise Exception(f"Failed to send init request: {e}")

            # Step 1.5: Read initialize response
            init_response = None
            while True:
                try:
                    line = process.stdout.readline()
                    if not line:
                        raise Exception("MCP server closed stdout before sending init response")

                    line = line.strip()
                    if line.startswith('{'):
                        response = json.loads(line)
                        if response.get('id') == 1:  # Our init request
                            init_response = response
                            break
                except json.JSONDecodeError:
                    continue

            if not init_response or 'result' not in init_response:
                raise Exception(f"Invalid init response: {init_response}")

            print(f"[MCP] Initialized successfully")

            # Step 1.6: Send initialized notification (required by MCP spec)
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }

            try:
                process.stdin.write(json.dumps(initialized_notification) + "\n")
                process.stdin.flush()
            except Exception as e:
                raise Exception(f"Failed to send initialized notification: {e}")

            # Step 2: Send tool call request
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            try:
                process.stdin.write(json.dumps(tool_request) + "\n")
                process.stdin.flush()
            except Exception as e:
                raise Exception(f"Failed to send tool request: {e}")

            # Read remaining output
            try:
                remaining_stdout, stderr = process.communicate(timeout=60)
                stdout = remaining_stdout
            except Exception as e:
                process.kill()
                raise Exception(f"Failed during communicate: {e}")

            # Parse response
            if stderr:
                print(f"[MCP] stderr: {stderr[:200]}")

            # Find JSON-RPC response with id=2 (our tool call)
            for line in stdout.split('\n'):
                line = line.strip()
                if line.startswith('{'):
                    try:
                        response = json.loads(line)
                        if response.get('id') == 2:  # Match our tool call request
                            if 'result' in response:
                                # Extract text from MCP response
                                result = response['result']
                                if isinstance(result, list) and len(result) > 0:
                                    if isinstance(result[0], dict) and 'text' in result[0]:
                                        return result[0]['text']
                                    return str(result[0])
                                return str(result)
                            elif 'error' in response:
                                raise Exception(f"MCP error: {response['error']}")
                    except json.JSONDecodeError:
                        continue

            raise Exception("No valid MCP response received")

        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("MCP server timeout")
        except Exception as e:
            raise Exception(f"MCP client error: {str(e)}")


# Singleton instance
_mcp_client = None

def get_mcp_client() -> MCPClient:
    """Get or create MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        # Configure MCP server connection
        server_command = os.getenv('MCP_SERVER_COMMAND', 'python')
        server_script = os.getenv('MCP_SERVER_SCRIPT', '/app/mcp_agent/agent.py')

        # Fallback to local path if not in container
        if not os.path.exists(server_script):
            local_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'mcp_agent', 'agent.py'
            )
            if os.path.exists(local_path):
                server_script = local_path

        print(f"[MCP Client] Using agent at: {server_script}")
        print(f"[MCP Client] Workspace path: {os.getenv('WORKSPACE_PATH', '/workspace')}")

        _mcp_client = MCPClient(
            server_command=server_command,
            server_args=[server_script],
            env={
                'WORKSPACE_PATH': os.getenv('WORKSPACE_PATH', '/workspace'),
                'CEREBRAS_API_KEY': os.getenv('CEREBRAS_API_KEY'),
                'CEREBRAS_API_URL': os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')
            }
        )
    return _mcp_client
