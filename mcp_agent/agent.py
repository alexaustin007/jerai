import os
import glob
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

WORKSPACE = os.getenv('WORKSPACE_PATH', '/workspace')
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
CEREBRAS_API_URL = os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')

server = Server("jerai-bug-fixer")


def read_file_content(file_path: str) -> str:
    """Read file from workspace"""
    full_path = os.path.join(WORKSPACE, file_path)
    try:
        with open(full_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"


def search_files(pattern: str) -> list:
    """Search for files matching pattern across all workspace directories"""
    search_pattern = os.path.join(WORKSPACE, '**', pattern)
    matches = glob.glob(search_pattern, recursive=True)
    # Return relative paths from workspace root
    return [os.path.relpath(m, WORKSPACE) for m in matches if os.path.isfile(m)]

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


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="read_code",
            description="Read source code file from workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to file in workspace"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="analyze_bug",
            description="Analyze bug using Cerebras AI (Llama 3.3 70B)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Bug title/description"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed bug description"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="generate_patch",
            description="Generate code patch using Llama 3.3 70B via Cerebras",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Bug title"
                    },
                    "analysis": {
                        "type": "string",
                        "description": "Bug analysis from analyze_bug tool"
                    }
                },
                "required": ["title", "analysis"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle MCP tool calls"""

    if name == "read_code":
        file_path = arguments["file_path"]
        content = read_file_content(file_path)
        return [TextContent(type="text", text=content)]

    elif name == "analyze_bug":
        title = arguments["title"]
        description = arguments.get("description", "")

        try:
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
                return [TextContent(type="text", text=analysis)]
            else:
                raise Exception(f'Cerebras API error: {response.status_code}')

        except Exception as e:
            mock_analysis = f"Mock analysis (Cerebras unavailable): Floating-point precision issue in cart.py. Use Decimal for money calculations. Error: {str(e)}"
            return [TextContent(type="text", text=mock_analysis)]

    elif name == "generate_patch":
        title = arguments["title"]
        analysis = arguments["analysis"]

        # Extract keywords from title to find relevant files
        keywords = []
        title_lower = title.lower()
        description_lower = analysis.lower()

        # Map common bug types to file patterns
        if any(word in title_lower for word in ['hover', 'zoom', 'image', 'animation', 'transition', 'scale']):
            keywords.extend(['App.css', 'style', 'css'])
        if any(word in title_lower for word in ['button', 'ui', 'css', 'style', 'layout', 'component']):
            keywords.extend(['App', 'component', 'css', 'tsx', 'jsx'])
        if any(word in title_lower for word in ['cart', 'checkout', 'payment', 'price', 'total']):
            keywords.extend(['cart', 'checkout', 'payment'])
        if any(word in title_lower for word in ['api', 'endpoint', 'route', 'backend']):
            keywords.extend(['routes', 'api', 'service'])
        if any(word in title_lower for word in ['database', 'model', 'schema', 'table']):
            keywords.extend(['models', 'schema'])

        # Search for relevant files
        relevant_files = search_by_keywords(keywords) if keywords else []

        # Fallback: if no keywords matched, try generic search
        if not relevant_files:
            relevant_files = search_files('*.py') + search_files('*.tsx') + search_files('*.jsx')
            relevant_files = relevant_files[:3]  # Limit to first 3 files

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

        try:
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
                return [TextContent(type="text", text=patch)]
            else:
                raise Exception(f'Cerebras API error: {response.status_code}')

        except Exception as e:
            error_message = f"""ERROR: Failed to generate patch.

Reason: {str(e)}

The AI service is currently unavailable. Please try again later or contact support.

For manual fix, refer to the Analysis section above for suggested approach."""

            return [TextContent(type="text", text=error_message)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run MCP server using stdio transport"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
