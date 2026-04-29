from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import User
from app.routes.deps import get_current_user
from app.schemas.evaluation import EvaluationRequest, EvaluationRunOut
from app.services.evaluation_service import evaluation_service


router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.post("/run", response_model=EvaluationRunOut)
def run_evaluation(
    payload: EvaluationRequest,
    _: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    return evaluation_service.run(db, payload.model_mode, payload.dataset)


@router.get("/results", response_model=list[EvaluationRunOut])
def list_results(_: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    return evaluation_service.list_results(db)


@router.get("/results/{run_id}", response_model=EvaluationRunOut)
def get_result(
    run_id: str,
    _: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    result = evaluation_service.get_result(db, run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return result

