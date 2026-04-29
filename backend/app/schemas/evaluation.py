from datetime import datetime

from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    model_mode: str = "hybrid_memory"
    dataset: str = "Demo"


class EvaluationMetricOut(BaseModel):
    metric_name: str
    metric_value: float


class EvaluationRunOut(BaseModel):
    run_id: str
    model_mode: str
    dataset: str
    metrics: dict[str, float]
    notes: str
    created_at: datetime


class EvaluationLogOut(BaseModel):
    id: int
    run_id: str
    model_mode: str
    dataset: str
    metric_name: str
    metric_value: float
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}

