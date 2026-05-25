.PHONY: install test lint run-api ingest-sample build-index eval docker-up

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -q

lint:
	ruff check rag_project tests api
	black --check rag_project tests api || true

run-api:
	uvicorn rag_project.api.app:app --host 0.0.0.0 --port 8000 --reload

ingest-sample:
	python -m rag_project.workers.ingestion_worker --source examples/docs --tenant-id default --collection-id default

build-index:
	python -m rag_project.workers.indexing_worker --collection-id default --mode incremental

eval:
	python -m rag_project.evals.run_eval --dataset ./evals/golden.jsonl --output ./artifacts/evals/report.json

docker-up:
	docker compose up --build -d
