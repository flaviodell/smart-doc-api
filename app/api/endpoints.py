import redis
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.interaction import AIInteraction
from ..schemas.request import AIRequest
from ..services.ai_service import AIService
from ..core.config import settings

router = APIRouter()

cache = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.post("/process")
async def process_ai_task(request: AIRequest, db: Session = Depends(get_db)):
    cache_key = f"{request.task}:{request.text[:50]}" 

    cached_response = cache.get(cache_key)
    if cached_response:
        return {
            "id": "from_cache",
            "task": request.task,
            "response": cached_response,
            "status": "success (cached)"
        }

    try:
        response_text = AIService.process_task(
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
        model_used="mixed-hybrid"
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
