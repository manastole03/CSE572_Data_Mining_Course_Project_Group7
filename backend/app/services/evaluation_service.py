from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy.orm import Session as OrmSession

from app.models import EvaluationLog


MODE_FACTORS = {
    "no_memory": 0.45,
    "naive_rag": 0.62,
    "lora_only": 0.68,
    "hybrid_memory": 0.84,
}

DATASET_FACTORS = {
    "Demo": 1.0,
    "MathDial": 0.95,
    "PersonaMem-v2": 0.9,
    "LoCoMo": 0.88,
}


class EvaluationService:
    def run(self, db: OrmSession, model_mode: str, dataset: str) -> dict:
        run_id = f"eval_{uuid.uuid4().hex[:12]}"
        mode_factor = MODE_FACTORS.get(model_mode, 0.6)
        dataset_factor = DATASET_FACTORS.get(dataset, 1.0)
        metrics = {
            "memory_precision": round(min(0.98, mode_factor * dataset_factor), 3),
            "memory_recall": round(min(0.96, mode_factor * dataset_factor + 0.05), 3),
            "personalization_score": round(min(0.97, mode_factor + (0.08 if model_mode == "hybrid_memory" else 0)), 3),
            "forgetting_leakage_rate": round(max(0.01, 0.22 - mode_factor / 5), 3),
            "latency_ms": round(420 + (120 if model_mode == "hybrid_memory" else 40), 2),
            "token_usage": round(700 + (250 if model_mode in {"naive_rag", "hybrid_memory"} else 80), 2),
            "storage_growth": round(1.0 + (1.8 if model_mode == "hybrid_memory" else 0.4), 2),
        }
        now = datetime.utcnow()
        for name, value in metrics.items():
            db.add(
                EvaluationLog(
                    run_id=run_id,
                    model_mode=model_mode,
                    dataset=dataset,
                    metric_name=name,
                    metric_value=float(value),
                    notes="Mock MVP metric; service is structured for real benchmark integration.",
                    created_at=now,
                )
            )
        db.commit()
        return {
            "run_id": run_id,
            "model_mode": model_mode,
            "dataset": dataset,
            "metrics": metrics,
            "notes": "Mock MVP metric; service is structured for real benchmark integration.",
            "created_at": now,
        }

    def list_results(self, db: OrmSession) -> list[dict]:
        rows = db.query(EvaluationLog).order_by(EvaluationLog.created_at.desc()).all()
        grouped: dict[str, dict] = {}
        for row in rows:
            item = grouped.setdefault(
                row.run_id,
                {
                    "run_id": row.run_id,
                    "model_mode": row.model_mode,
                    "dataset": row.dataset,
                    "metrics": {},
                    "notes": row.notes,
                    "created_at": row.created_at,
                },
            )
            item["metrics"][row.metric_name] = row.metric_value
        return list(grouped.values())

    def get_result(self, db: OrmSession, run_id: str) -> dict | None:
        rows = db.query(EvaluationLog).filter(EvaluationLog.run_id == run_id).all()
        if not rows:
            return None
        first = rows[0]
        return {
            "run_id": first.run_id,
            "model_mode": first.model_mode,
            "dataset": first.dataset,
            "metrics": {row.metric_name: row.metric_value for row in rows},
            "notes": first.notes,
            "created_at": first.created_at,
        }


evaluation_service = EvaluationService()

