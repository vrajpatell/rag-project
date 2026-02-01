# Build stage for Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# Final stage
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary modules
COPY api /app/api
COPY rag_pipeline /app/rag_pipeline
COPY vector_store /app/vector_store

# Copy built frontend assets to the api directory where main.py expects them
COPY --from=frontend-builder /app/frontend/dist /app/api/static

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
