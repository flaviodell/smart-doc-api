import redis
import json
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models.interaction import AIInteraction
from ..schemas.request import AIRequest
from ..services.ai_service import AIService
from ..core.config import settings

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
    cache_key = make_cache_key(request.task, request.text, request.question)

    cached_response = cache.get(cache_key)
    if cached_response:
        return {
            "id": "from_cache",
            "task": request.task,
            "response": cached_response,
            "status": "success (cached)"
        }

    try:
        response_text, model_used = AIService.process_task(
            task=request.task,
            text=request.text,
            question=request.question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_interaction = AIInteraction(
        task_type=request.task,
        input_text=request.text,
        output_text=response_text,
        model_used=model_used
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

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