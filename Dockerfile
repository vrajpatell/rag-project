FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY rag_project ./rag_project
COPY api ./api
COPY evals ./evals
COPY examples ./examples

RUN pip install --no-cache-dir -r requirements.txt

ENV APP_ENV=local
EXPOSE 8000

CMD ["uvicorn", "rag_project.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
