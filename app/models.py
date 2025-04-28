from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    router_name = Column(String, nullable=False)
    source_ip = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
