FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .
COPY http_server.py .

ENV WORKSPACE_PATH=/workspace
EXPOSE 9000

CMD ["python", "http_server.py"]
