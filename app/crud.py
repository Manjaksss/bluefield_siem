
from app.database import SessionLocal
from app import models

def insert_event(router_name: str, source_ip: str, event_type: str, description: str):
    db = SessionLocal()
    event = models.Event(
        router_name=router_name,
        source_ip=source_ip,
        event_type=event_type,
        description=description,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    db.close()

def get_events():
    db = SessionLocal()
    events = db.query(models.Event).order_by(models.Event.timestamp.desc()).all()
    db.close()
    return events

def get_stats(events):
    stats = {}
    routers = {}
    total = 0

    for event in events:
        routers.setdefault(event.router_name, 0)
        routers[event.router_name] += 1
        total += 1

    stats['total_events'] = total
    stats['events_per_router'] = routers
    return stats
