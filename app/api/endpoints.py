from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.interaction import AIInteraction
from ..schemas.request import AIRequest
from ..services.ai_service import AIService

router = APIRouter()

@router.post("/process")
async def process_ai_task(request: AIRequest, db: Session = Depends(get_db)):
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
        model_used="llama3-8b-8192"
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return {
        "id": new_interaction.id,
        "task": request.task,
        "response": response_text
    }