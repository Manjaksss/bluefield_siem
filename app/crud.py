from app import models, database
from sqlalchemy.orm import Session
from datetime import datetime

def insert_event(router_name: str, source_ip: str, event_type: str, description: str):
    db = Session(bind=database.engine)
    event = models.Event(
        router_name=router_name,
        source_ip=source_ip,
        event_type=event_type,
        description=description,
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.close()

def get_events():
    db = Session(bind=database.engine)
    events = db.query(models.Event).order_by(models.Event.timestamp.desc()).all()
    db.close()
    return events

def get_stats(events):
    total = 0
    router_counter = {}
    event_type_counter = {}

    for event in events:
        router_name = event.router_name or "Unknown"
        event_type = event.event_type or "Unknown"

        router_counter.setdefault(router_name, 0)
        router_counter[router_name] += 1

        event_type_counter.setdefault(event_type, 0)
        event_type_counter[event_type] += 1

        total += 1

    return {
        "total_events": total,
        "router_counter": router_counter,
        "event_type_counter": event_type_counter
    }