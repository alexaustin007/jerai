from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
MCP_AGENT_URL = os.getenv('MCP_AGENT_URL', 'http://mcp_agent:9000')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "mcp-gateway"})

@app.route('/generate-patch', methods=['POST'])
def generate_patch():
    """Proxy request to MCP Agent running Llama"""
    try:
        data = request.json
        print(f"Gateway received request: {data.get('title', 'N/A')}")

        response = requests.post(
            f"{MCP_AGENT_URL}/generate-patch",
            json=data,
            timeout=120
        )

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
