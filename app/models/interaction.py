from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from ..core.database import Base

class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)  # summarization, qa, classification
    input_text = Column(Text)
    output_text = Column(Text)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)