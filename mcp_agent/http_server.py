#!/usr/bin/env python3
"""
HTTP wrapper for MCP agent - provides REST API endpoints
"""
import os
import glob
import requests
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
import uvicorn

app = Starlette()

WORKSPACE = os.getenv('WORKSPACE_PATH', '/workspace')
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
CEREBRAS_API_URL = os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')

def read_file_content(file_path: str) -> str:
    """Read file from workspace"""
    full_path = os.path.join(WORKSPACE, file_path)
    try:
        with open(full_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def search_by_keywords(keywords: list) -> list:
    """Search for files containing any of the keywords in their path or name"""
    matches = []
    for root, dirs, files in os.walk(WORKSPACE):
        # Skip node_modules, venv, __pycache__
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git']]

        for file in files:
            # Skip non-code files
            if not file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html')):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, WORKSPACE)

            # Check if any keyword matches the file path or name
            for keyword in keywords:
                if keyword.lower() in rel_path.lower() or keyword.lower() in file.lower():
                    matches.append(rel_path)
                    break

    return matches[:10]  # Limit to 10 most relevant files

@app.route('/health', methods=['GET'])
async def health_check(request: Request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "mcp-agent"})

@app.route('/tools/analyze_bug', methods=['POST'])
async def analyze_bug_endpoint(request: Request):
    """Analyze bug endpoint"""
    try:
        data = await request.json()
        title = data.get('title', '')
        description = data.get('description', '')
        
        if not CEREBRAS_API_KEY:
            raise Exception("CEREBRAS_API_KEY not set")
            
        response = requests.post(
            CEREBRAS_API_URL,
            headers={
                'Authorization': f'Bearer {CEREBRAS_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b',
                'messages': [{
                    'role': 'user',
                    'content': f"""Analyze this bug and provide a clear, structured analysis for an engineer.

Bug Title: {title}
Description: {description or "Application bug"}

Codebase:
- Backend: Python/Flask (backend/)
- Frontend: React/TS (frontend/, ecommerce-app/)
- Styling: CSS in src/ directories

Provide a structured analysis in this exact format:

ROOT CAUSE:
[1-2 sentences explaining what's wrong]

AFFECTED FILES:
[List exact file paths, one per line, e.g., "ecommerce-app/src/App.css"]

FIX APPROACH:
[2-3 sentences explaining what changes are needed]

Be specific. Mention exact file paths and CSS properties/code elements."""
                }],
                'max_tokens': 500,
                'temperature': 0.7
            },
            timeout=10
        )
        
        if response.status_code == 200:
            analysis = response.json()['choices'][0]['message']['content']
            return JSONResponse({
                'success': True,
                'analysis': analysis
            })
        else:
            raise Exception(f'Cerebras API error: {response.status_code}')
            
    except Exception as e:
        mock_analysis = f"Mock analysis (Cerebras unavailable): Floating-point precision issue in cart.py. Use Decimal for money calculations. Error: {str(e)}"
        return JSONResponse({
            'success': True,
            'analysis': mock_analysis
        })

@app.route('/tools/generate_patch', methods=['POST'])
async def generate_patch_endpoint(request: Request):
    """Generate patch endpoint"""
    try:
        data = await request.json()
        title = data.get('title', '')
        analysis = data.get('analysis', '')
        
        if not CEREBRAS_API_KEY:
            raise Exception("CEREBRAS_API_KEY not set")
        
        # Extract keywords from title to find relevant files
        keywords = []
        title_lower = title.lower()
        
        # Map common bug types to file patterns
        if any(word in title_lower for word in ['hover', 'zoom', 'image', 'animation', 'transition', 'scale']):
            keywords.extend(['App.css', 'style', 'css'])
        if any(word in title_lower for word in ['button', 'ui', 'css', 'style', 'layout', 'component']):
            keywords.extend(['App', 'component', 'css', 'tsx', 'jsx'])
        if any(word in title_lower for word in ['cart', 'checkout', 'payment', 'price', 'total']):
            keywords.extend(['cart', 'checkout', 'payment'])
        
        # Search for relevant files
        relevant_files = search_by_keywords(keywords) if keywords else []
        
        code_context = ""
        if relevant_files:
            for f in relevant_files[:3]:  # Limit to 3 most relevant files
                code_content = read_file_content(f)
                code_context += f"\n--- File: {f} ---\n{code_content[:2000]}\n"  # Limit content per file
        else:
            code_context = "No relevant files found in workspace."

        prompt = f"""Generate a clean code patch to fix this bug.

Bug: {title}

Analysis: {analysis}

Current Code:
{code_context}

Generate a unified diff patch with this format:

--- a/path/to/file.ext
+++ b/path/to/file.ext
@@ -line,count +line,count @@
 unchanged line
-line to remove
+line to add
 unchanged line

RULES:
- Show only minimal changes needed
- Use correct file paths from the code above
- For CSS: add transition, transform, etc.
- For Python: follow best practices
- Clean, readable format

Output ONLY the diff. No explanations."""

        response = requests.post(
            CEREBRAS_API_URL,
            headers={
                'Authorization': f'Bearer {CEREBRAS_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b',
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }],
                'max_tokens': 1000,
                'temperature': 0.3
            },
            timeout=30
        )

        if response.status_code == 200:
            patch = response.json()['choices'][0]['message']['content']
            return JSONResponse({
                'success': True,
                'patch': patch
            })
        else:
            raise Exception(f'Cerebras API error: {response.status_code}')
            
    except Exception as e:
        error_message = f"""ERROR: Failed to generate patch.

Reason: {str(e)}

The AI service is currently unavailable. Please try again later or contact support.

For manual fix, refer to the Analysis section above for suggested approach."""

        return JSONResponse({
            'success': False,
            'patch': error_message,
            'error': str(e)
        }, status_code=500)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 9000))
    print(f"Starting MCP HTTP server on port {port}")
    print(f"Workspace: {os.getenv('WORKSPACE_PATH', '/workspace')}")
    print(f"Cerebras API: {'SET' if os.getenv('CEREBRAS_API_KEY') else 'NOT SET'}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)