from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from ..core.database import Base


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)
    input_text = Column(Text)
    output_text = Column(Text)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIMetric(Base):
    __tablename__ = "ai_metrics"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)
    model_used = Column(String)
    input_length = Column(Integer)
    output_length = Column(Integer)
    latency_ms = Column(Integer)
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)