from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from backend.app.services.store import get_store, StoreError

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

def collection(name):
    try: return get_store().list(name)
    except StoreError as exc: raise HTTPException(503, str(exc))
    except Exception as exc: raise HTTPException(500, f"Analytics query failed: {exc}")

@router.get("/dashboard")
def dashboard():
    drones, batteries, missions, flights, maintenance = [collection(x) for x in ("drones","batteries","missions","flights","maintenance")]
    now = datetime.now(timezone.utc)
    month = now.strftime("%Y-%m")
    return {
        "total_drones": len([d for d in drones if d.get("status") != "RETIRED"]),
        "total_batteries": len(batteries),
        "fleets_this_month": len([m for m in missions if str(m.get("created_at", "")).startswith(month)]),
        "total_fleets": len(missions),
        "total_flying_time_minutes": round(sum(float(f.get("duration_minutes", 0) or 0) for f in flights), 2),
        "active_missions": len([m for m in missions if m.get("status") in ("SCHEDULED", "IN_PROGRESS")]),
        "critical_batteries": len([b for b in batteries if b.get("status") == "CRITICAL"]),
        "overdue_maintenance": len([m for m in maintenance if m.get("status") == "OVERDUE"]),
    }

@router.get("/kpis")
def kpis():
    return dashboard()

@router.get("/missions")
def mission_analytics():
    missions = collection("missions")
    statuses = {}
    for item in missions: statuses[item.get("status", "UNKNOWN")] = statuses.get(item.get("status", "UNKNOWN"), 0) + 1
    return {"total": len(missions), "by_status": statuses}

@router.get("/flights")
def flight_analytics():
    flights = collection("flights")
    return {"total": len(flights), "total_duration_minutes": round(sum(float(x.get("duration_minutes", 0) or 0) for x in flights), 2), "total_distance_km": round(sum(float(x.get("distance_km", 0) or 0) for x in flights), 2), "battery_consumed_percentage": round(sum(float(x.get("battery_consumed_percentage", 0) or 0) for x in flights), 2)}

@router.get("/batteries")
def battery_analytics():
    batteries = collection("batteries")
    return {"total": len(batteries), "low_batteries": len([x for x in batteries if x.get("status") == "LOW"]), "critical_batteries": len([x for x in batteries if x.get("status") == "CRITICAL"]), "average_health": round(sum(float(x.get("health_percentage", 0) or 0) for x in batteries)/len(batteries), 2) if batteries else 0}

@router.get("/maintenance")
def maintenance_analytics():
    rows = collection("maintenance")
    return {"total": len(rows), "overdue": len([x for x in rows if x.get("status") == "OVERDUE"]), "by_priority": {p: len([x for x in rows if x.get("priority") == p]) for p in ("LOW","MEDIUM","HIGH","CRITICAL")}}

@router.get("/trends")
def trends():
    flights = collection("flights")
    return {"flights": flights[-30:]}
