import redis
import hashlib
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.interaction import AIInteraction, AIMetric
from ..schemas.request import AIRequest
from ..services.ai_service import AIService
from ..core.config import settings
from ..core.logging import get_logger

log = get_logger(__name__)
router = APIRouter()

cache = redis.from_url(settings.REDIS_URL, decode_responses=True)


def make_cache_key(task: str, text: str, question: str = None) -> str:
    """
    Build a collision-safe cache key using SHA256.
    Truncating text to N chars causes false cache hits when two different
    texts share the same prefix — hashing the full content avoids this.
    """
    raw = f"{task}:{text}"
    if question:
        raw += f":{question}"
    return hashlib.sha256(raw.encode()).hexdigest()


@router.post("/process")
async def process_ai_task(request: AIRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    cache_key = make_cache_key(request.task, request.text, request.question)

    cached_response = cache.get(cache_key)
    if cached_response:
        latency_ms = int((time.time() - start_time) * 1000)
        log.info(f"Cache hit | task={request.task} | key={cache_key[:12]}...")

        metric = AIMetric(
            task_type=request.task,
            model_used="cache",
            input_length=len(request.text),
            output_length=len(cached_response),
            latency_ms=latency_ms,
            cached=True,
        )
        db.add(metric)
        db.commit()

        return {
            "id": "from_cache",
            "task": request.task,
            "response": cached_response,
            "status": "success (cached)"
        }

    log.info(f"Cache miss | task={request.task} | input_len={len(request.text)}")

    try:
        response_text, model_used = AIService.process_task(
            task=request.task,
            text=request.text,
            question=request.question
        )
    except Exception as e:
        log.error(f"AI service error | task={request.task} | error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    latency_ms = int((time.time() - start_time) * 1000)
    log.info(f"AI response | task={request.task} | model={model_used} | latency={latency_ms}ms")

    new_interaction = AIInteraction(
        task_type=request.task,
        input_text=request.text,
        output_text=response_text,
        model_used=model_used
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    metric = AIMetric(
        task_type=request.task,
        model_used=model_used,
        input_length=len(request.text),
        output_length=len(response_text),
        latency_ms=latency_ms,
        cached=False,
    )
    db.add(metric)
    db.commit()

    cache.setex(cache_key, 3600, response_text)

    return {
        "id": new_interaction.id,
        "task": request.task,
        "response": response_text,
        "status": "success (new)"
    }


@router.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Return the most recent AI interactions stored in PostgreSQL.
    Demonstrates that the database is actually used as persistent storage.
    """
    interactions = (
        db.query(AIInteraction)
        .order_by(AIInteraction.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": i.id,
            "task_type": i.task_type,
            "input_text": i.input_text[:100] + "..." if len(i.input_text) > 100 else i.input_text,
            "output_text": i.output_text[:200] + "..." if len(i.output_text) > 200 else i.output_text,
            "model_used": i.model_used,
            "created_at": i.created_at.isoformat(),
        }
        for i in interactions
    ]


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Return aggregate performance metrics from PostgreSQL.
    Shows total requests, cache hit rate, and average latency by task type.
    """
    total = db.query(AIMetric).count()
    cached_count = db.query(AIMetric).filter(AIMetric.cached == True).count()

    by_task = (
        db.query(
            AIMetric.task_type,
            func.count(AIMetric.id).label("count"),
            func.avg(AIMetric.latency_ms).label("avg_latency_ms"),
        )
        .group_by(AIMetric.task_type)
        .all()
    )

    return {
        "total_requests": total,
        "cache_hit_rate_pct": round(cached_count / total * 100, 1) if total > 0 else 0,
        "by_task": [
            {
                "task": row.task_type,
                "count": row.count,
                "avg_latency_ms": round(row.avg_latency_ms, 1),
            }
            for row in by_task
        ],
    }