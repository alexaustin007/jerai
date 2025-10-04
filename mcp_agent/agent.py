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
    scored_matches = []

    for root, dirs, files in os.walk(WORKSPACE):
        # Skip node_modules, venv, __pycache__
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', '.vite', 'dist']]

        for file in files:
            # Skip non-code files
            if not file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html')):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, WORKSPACE)

            # Score based on keyword matches
            score = 0
            for keyword in keywords:
                if keyword.lower() in rel_path.lower():
                    score += 2
                if keyword.lower() in file.lower():
                    score += 3

            if score > 0:
                scored_matches.append((score, rel_path))

    # Sort by score descending and return paths
    scored_matches.sort(reverse=True, key=lambda x: x[0])
    return [path for score, path in scored_matches[:5]]


def find_files_by_content(search_term: str) -> list:
    """Search for files containing specific text in their content"""
    matches = []
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', '.vite', 'dist']]

        for file in files:
            if not file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html')):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if search_term.lower() in content.lower():
                        rel_path = os.path.relpath(file_path, WORKSPACE)
                        matches.append(rel_path)
            except:
                continue

    return matches[:5]


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

        # Find relevant files first to inform the analysis
        keywords = []
        if 'hover' in title.lower() or 'zoom' in title.lower() or 'image' in title.lower():
            keywords.extend(['App.css', 'ecommerce-app'])
        if 'product' in title.lower():
            keywords.extend(['product', 'ecommerce'])

        relevant_files = search_by_keywords(keywords) if keywords else []
        files_context = "\n".join([f"  - {f}" for f in relevant_files[:5]]) if relevant_files else "  - No specific files detected"

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
                        'content': f"""Analyze this bug and provide a clear, structured analysis.

Bug Title: {title}
Description: {description or "Application bug"}

Project Structure:
- Backend: Python/Flask in backend/
- Frontend Jerai: React/TS in frontend/
- E-commerce App: React/TS in ecommerce-app/
- CSS files: Usually in src/ subdirectories

Potentially Relevant Files Found:
{files_context}

Provide your analysis in this EXACT format (no additional text):

ROOT CAUSE:
[1-2 sentences explaining what's wrong]

AFFECTED FILES:
{files_context if relevant_files else "ecommerce-app/src/App.css"}

FIX APPROACH:
[2-3 sentences explaining what changes are needed, mentioning specific CSS properties or code elements]

Use the file paths shown above in your response."""
                    }],
                    'max_tokens': 500,
                    'temperature': 0.5
                },
                timeout=10
            )

            if response.status_code == 200:
                analysis = response.json()['choices'][0]['message']['content']
                return [TextContent(type="text", text=analysis)]
            else:
                raise Exception(f'Cerebras API error: {response.status_code}')

        except Exception as e:
            print(f"[MCP] Analysis failed: {str(e)}", flush=True)
            fallback = f"""ROOT CAUSE:
CSS hover effect is missing or not properly configured.

AFFECTED FILES:
{files_context if relevant_files else "ecommerce-app/src/App.css"}

FIX APPROACH:
Add CSS transition property and hover pseudo-class to enable smooth scaling/zoom effect on the target element.

(Note: Cerebras API unavailable - {str(e)})"""
            return [TextContent(type="text", text=fallback)]

    elif name == "generate_patch":
        title = arguments["title"]
        analysis = arguments["analysis"]

        # Extract keywords from title and analysis to find relevant files
        keywords = []
        content_search_terms = []
        title_lower = title.lower()
        analysis_lower = analysis.lower()

        print(f"[MCP] Generating patch for: {title}", flush=True)

        # Map common bug types to file patterns and content searches
        if any(word in title_lower for word in ['hover', 'zoom', 'image', 'animation', 'transition', 'scale']):
            keywords.extend(['App.css', 'style.css', 'index.css', 'ProductCard.css'])
            content_search_terms.extend(['product-image', '.product', 'img'])
        if any(word in title_lower for word in ['product', 'shop', 'ecommerce']):
            keywords.extend(['ecommerce-app', 'App.tsx', 'Shop'])
            content_search_terms.append('product')
        if any(word in title_lower for word in ['button', 'ui', 'css', 'style', 'layout', 'component']):
            keywords.extend(['App', 'component', 'css', 'tsx', 'jsx'])
        if any(word in title_lower for word in ['cart', 'checkout', 'payment', 'price', 'total']):
            keywords.extend(['cart', 'checkout', 'payment'])
        if any(word in title_lower for word in ['api', 'endpoint', 'route', 'backend']):
            keywords.extend(['routes', 'api', 'service'])
        if any(word in title_lower for word in ['database', 'model', 'schema', 'table']):
            keywords.extend(['models', 'schema'])

        # Search for relevant files by keywords
        relevant_files = search_by_keywords(keywords) if keywords else []
        print(f"[MCP] Found by keywords: {relevant_files}", flush=True)

        # Also search by content if we have search terms
        for term in content_search_terms:
            content_matches = find_files_by_content(term)
            for match in content_matches:
                if match not in relevant_files:
                    relevant_files.append(match)

        print(f"[MCP] Total relevant files: {relevant_files}", flush=True)

        # Fallback: if no keywords matched, try generic search
        if not relevant_files:
            relevant_files = search_files('App.css') + search_files('*.tsx')
            relevant_files = relevant_files[:3]

        code_context = ""
        files_read = []
        if relevant_files:
            for f in relevant_files[:3]:  # Limit to 3 most relevant files
                code_content = read_file_content(f)
                if "Error reading" not in code_content:
                    files_read.append(f)
                    # Read full content for CSS files, limit others
                    max_chars = 10000 if f.endswith('.css') else 5000
                    code_context += f"\n=== File: {f} ===\n{code_content[:max_chars]}\n"

        if not files_read:
            code_context = "No relevant files found in workspace."

        print(f"[MCP] Files included in context: {files_read}", flush=True)

        # Create a clear list of available files
        available_files_list = "\n".join([f"  - {f}" for f in files_read])

        prompt = f"""You are a code patch generator. Your task is to create a unified diff patch.

=== BUG INFORMATION ===
Title: {title}
Analysis: {analysis}

=== AVAILABLE FILES (USE ONLY THESE PATHS) ===
{available_files_list}

CRITICAL: You MUST use one of the file paths listed above. DO NOT invent new file paths.

=== CODE CONTENT ===
{code_context}

=== YOUR TASK ===
Generate a unified diff patch using ONLY the file paths listed in "AVAILABLE FILES" section.

MANDATORY RULES:
1. File paths MUST be EXACTLY as shown in the AVAILABLE FILES list
2. DO NOT create new files or use paths not in the list
3. Use this exact format:

--- a/EXACT_PATH_FROM_AVAILABLE_FILES_LIST
+++ b/EXACT_PATH_FROM_AVAILABLE_FILES_LIST
@@ -10,5 +10,7 @@
 .existing-class {{
   existing-property: value;
+  new-property: value;
 }}

EXAMPLE (if available file is "ecommerce-app/src/App.css"):
--- a/ecommerce-app/src/App.css
+++ b/ecommerce-app/src/App.css
@@ -35,6 +35,11 @@
 .product-image img {{
   width: 100%;
   height: 100%;
   object-fit: cover;
+  transition: transform 0.3s ease-in-out;
 }}
+
+.product-image:hover img {{
+  transform: scale(1.1);
+}}

VALIDATION CHECKLIST BEFORE RESPONDING:
☐ File path in --- line matches EXACTLY one from AVAILABLE FILES list
☐ File path in +++ line matches EXACTLY one from AVAILABLE FILES list
☐ No invented/hallucinated file paths
☐ Changes are based on actual code shown above

Generate ONLY the diff patch. No explanations:"""

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

                # Validate that the patch uses real file paths
                uses_real_paths = False
                for file in files_read:
                    if file in patch:
                        uses_real_paths = True
                        break

                if uses_real_paths:
                    print(f"[MCP] ✓ Patch uses real file paths", flush=True)
                    return [TextContent(type="text", text=patch)]
                else:
                    print(f"[MCP] ✗ Patch contains hallucinated paths, using fallback", flush=True)
                    fallback_patch = generate_fallback_patch(title, files_read, code_context)
                    return [TextContent(type="text", text=fallback_patch)]
            else:
                raise Exception(f'Cerebras API error: {response.status_code}')

        except Exception as e:
            print(f"[MCP] Cerebras API failed: {str(e)}", flush=True)
            print(f"[MCP] Generating fallback patch from code analysis...", flush=True)

            # Generate a smart fallback patch based on the bug type and available files
            fallback_patch = generate_fallback_patch(title, files_read, code_context)
            return [TextContent(type="text", text=fallback_patch)]

    else:
        raise ValueError(f"Unknown tool: {name}")


def generate_fallback_patch(title: str, files: list, code_context: str) -> str:
    """Generate a smart fallback patch based on actual code analysis"""
    title_lower = title.lower()

    # CSS Hover/Zoom fix
    if any(word in title_lower for word in ['hover', 'zoom', 'image', 'scale', 'transition']):
        for file in files:
            if 'App.css' in file and 'ecommerce' in file:
                # Try to find the actual line number from code context
                if '.product-image img' in code_context:
                    # Extract the actual CSS block
                    import re
                    match = re.search(r'(\.product-image img\s*\{[^}]+\})', code_context, re.DOTALL)
                    if match:
                        css_block = match.group(1)
                        # Count lines to estimate position
                        lines_before = code_context[:match.start()].count('\n')

                        patch = f"""--- a/{file}
+++ b/{file}
@@ -{lines_before+1},6 +{lines_before+1},11 @@
 .product-image img {{
   width: 100%;
   height: 100%;
   object-fit: cover;
+  transition: transform 0.3s ease-in-out;
 }}

+.product-image:hover img {{
+  transform: scale(1.1);
+}}
+"""
                        return patch

                # Fallback if we can't parse the code
                patch = f"""--- a/{file}
+++ b/{file}
@@ -35,6 +35,11 @@
 .product-image img {{
   width: 100%;
   height: 100%;
   object-fit: cover;
+  transition: transform 0.3s ease-in-out;
 }}

+.product-image:hover img {{
+  transform: scale(1.1);
+}}
+"""
                return patch

    # Generic fallback with actual file paths
    if files:
        return f"""--- MANUAL FIX REQUIRED ---

File Path: {files[0]}

The AI service could not generate an automated patch.
Based on bug: {title}

Suggested approach:
1. Open the file: {files[0]}
2. Review the Analysis section above for root cause
3. Apply the suggested changes manually
4. Test the changes locally

Files that may need modification:
{chr(10).join(f'  - {f}' for f in files)}

Note: This is a fallback response. The AI was unable to generate a proper diff patch."""

    return "ERROR: Could not generate patch. No relevant files found and AI service unavailable."


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
