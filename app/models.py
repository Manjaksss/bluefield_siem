
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    router_name = Column(String)
    source_ip = Column(String)
    event_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
