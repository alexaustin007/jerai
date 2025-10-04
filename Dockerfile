FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ .

# Copy MCP agent for workspace access
COPY mcp_agent/ ./mcp_agent/

# Copy other directories for MCP workspace access
COPY frontend/ ./workspace/frontend/
COPY ecommerce-app/ ./workspace/ecommerce-app/

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_PATH=/app/workspace

EXPOSE 8000

CMD ["python", "app.py"]
