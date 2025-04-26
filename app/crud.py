
from app import database, models
from collections import Counter
from datetime import datetime, timedelta

db = database.SessionLocal()

def create_event(router_name, source_ip, event_type, description):
    event = models.Event(
        router_name=router_name,
        source_ip=source_ip,
        event_type=event_type,
        description=description
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_events():
    return db.query(models.Event).order_by(models.Event.timestamp.desc()).all()

def get_stats():
    events = db.query(models.Event).all()
    router_counter = Counter([event.router_name for event in events])

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    weekly_count = db.query(models.Event).filter(models.Event.timestamp >= week_ago).count()
    monthly_count = db.query(models.Event).filter(models.Event.timestamp >= month_ago).count()

    return {
        "router_counter": router_counter,
        "weekly_count": weekly_count,
        "monthly_count": monthly_count
    }
