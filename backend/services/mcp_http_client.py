import os
import requests
from typing import Dict, Any

class MCPHTTPClient:
    """HTTP client for MCP agent service"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('MCP_GATEWAY_URL', 'http://localhost:9000')
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool via HTTP and return the result"""
        
        try:
            url = f"{self.base_url}/tools/{tool_name}"
            
            response = requests.post(
                url,
                json=arguments,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if tool_name == 'analyze_bug':
                        return data.get('analysis', 'No analysis returned')
                    elif tool_name == 'generate_patch':
                        return data.get('patch', 'No patch returned')
                    else:
                        return str(data)
                else:
                    raise Exception(f"MCP tool failed: {data.get('error', 'Unknown error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"MCP HTTP client error: {str(e)}")

# Singleton instance
_mcp_http_client = None

def get_mcp_http_client() -> MCPHTTPClient:
    """Get or create MCP HTTP client instance"""
    global _mcp_http_client
    if _mcp_http_client is None:
        gateway_url = os.getenv('MCP_GATEWAY_URL', 'http://localhost:9000')
        print(f"[MCP HTTP Client] Using gateway at: {gateway_url}")
        _mcp_http_client = MCPHTTPClient(gateway_url)
    return _mcp_http_client
