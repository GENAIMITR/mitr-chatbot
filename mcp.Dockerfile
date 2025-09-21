FROM python:3.11-slim
WORKDIR /app
COPY mcp.requirements.txt .
RUN pip install --no-cache-dir -r mcp.requirements.txt
COPY . .
EXPOSE 8081
CMD ["gunicorn", "-b", "0.0.0.0:8081", "mcp_server:app"]