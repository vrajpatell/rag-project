from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/evals", tags=["evals"])


class EvalRunRequest(BaseModel):
    dataset_path: str = "./evals/golden.jsonl"


@router.post("/run")
async def run_eval_endpoint(body: EvalRunRequest):
    from rag_project.evals.run_eval import run_eval

    report = run_eval(body.dataset_path)
    return report.model_dump()
