from fastapi import APIRouter, HTTPException, Query
from typing import Any
from backend.app.services.store import get_store, StoreError
from backend.app.schemas import DroneIn, BatteryIn, MissionIn, FlightIn, MaintenanceIn
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Fleet Operations"])
COLLECTIONS = {
    "drones": ("drones", DroneIn),
    "batteries": ("batteries", BatteryIn),
    "missions": ("missions", MissionIn),
    "flights": ("flights", FlightIn),
    "maintenance": ("maintenance", MaintenanceIn),
}

def safe(call):
    try:
        return call()
    except StoreError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {exc}")

def register_resource(name, collection, model):
    @router.get(f"/{name}", name=f"list_{name}")
    def list_items(search: str | None = None, status: str | None = None, sort_by: str = "created_at", sort_order: str = "desc"):
        rows = safe(lambda: get_store().list(collection))
        if search:
            q = search.casefold()
            rows = [r for r in rows if q in " ".join(str(v) for v in r.values()).casefold()]
        if status:
            rows = [r for r in rows if str(r.get("status", "")).upper() == status.upper()]
        rows.sort(key=lambda r: str(r.get(sort_by, "")), reverse=sort_order.lower() != "asc")
        return {"items": rows, "count": len(rows)}

    @router.post(f"/{name}", status_code=201, name=f"create_{name}")
    def create_item(payload: model):
        data = payload.model_dump(exclude_none=True)
        if name == "flights":
            try:
                start = datetime.fromisoformat(data["actual_start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(data["actual_end"].replace("Z", "+00:00"))
                if end <= start: raise HTTPException(422, "actual_end must be after actual_start")
                if data["end_battery_percentage"] > data["start_battery_percentage"]:
                    raise HTTPException(422, "end battery percentage cannot exceed start battery percentage")
                data["duration_minutes"] = round((end-start).total_seconds()/60, 2)
                data["battery_consumed_percentage"] = round(data["start_battery_percentage"]-data["end_battery_percentage"], 2)
            except ValueError:
                raise HTTPException(422, "Flight start and end must be valid ISO date-times")
        if name == "batteries":
            pct = data["battery_percentage"]
            data["status"] = "GOOD" if pct >= 80 else "NORMAL" if pct >= 50 else "LOW" if pct >= 20 else "CRITICAL"
            created = safe(lambda: get_store().create(collection, data))
            safe(lambda: get_store().create("battery_history", {"battery_id": created["id"], "drone_id": data["drone_id"], "serial_number": data["serial_number"], "battery_percentage": pct, "health_percentage": data.get("health_percentage", 100)}))
            return created
        return safe(lambda: get_store().create(collection, data))

    @router.get(f"/{name}/{{item_id}}", name=f"get_{name}")
    def get_item(item_id: str):
        item = safe(lambda: get_store().get(collection, item_id))
        if not item: raise HTTPException(404, f"{name[:-1].capitalize()} not found")
        return item

    @router.put(f"/{name}/{{item_id}}", name=f"update_{name}")
    def update_item(item_id: str, payload: dict[str, Any]):
        allowed = set(model.model_fields.keys())
        unknown = set(payload.keys()) - allowed
        if unknown:
            raise HTTPException(422, f"Unknown field(s): {', '.join(sorted(unknown))}")
        if name == "batteries" and "battery_percentage" in payload:
            pct = payload["battery_percentage"]
            if not isinstance(pct, (int, float)) or not 0 <= pct <= 100:
                raise HTTPException(422, "battery_percentage must be between 0 and 100")
            payload["status"] = "GOOD" if pct >= 80 else "NORMAL" if pct >= 50 else "LOW" if pct >= 20 else "CRITICAL"
        item = safe(lambda: get_store().update(collection, item_id, payload))
        if not item: raise HTTPException(404, f"{name[:-1].capitalize()} not found")
        if name == "batteries" and "battery_percentage" in payload:
            safe(lambda: get_store().create("battery_history", {"battery_id": item_id, "drone_id": item.get("drone_id"), "serial_number": item.get("serial_number"), "battery_percentage": item["battery_percentage"], "health_percentage": item.get("health_percentage", 100)}))
        return item

    @router.delete(f"/{name}/{{item_id}}", name=f"delete_{name}")
    def delete_item(item_id: str):
        if name == "drones":
            item = safe(lambda: get_store().update(collection, item_id, {"status": "INACTIVE"}))
            if not item: raise HTTPException(404, "Drone not found")
            return {"ok": True, "id": item_id, "status": "INACTIVE", "deactivated": True}
        deleted = safe(lambda: get_store().delete(collection, item_id))
        if not deleted: raise HTTPException(404, f"{name[:-1].capitalize()} not found")
        return {"ok": True, "id": item_id}

for key, (collection, model) in COLLECTIONS.items():
    register_resource(key, collection, model)

@router.get("/batteries/{battery_id}/history")
def battery_history(battery_id: str):
    rows = safe(lambda: get_store().list("battery_history"))
    return {"items": [r for r in rows if r.get("battery_id") == battery_id or r.get("serial_number") == battery_id], "count": len([r for r in rows if r.get("battery_id") == battery_id or r.get("serial_number") == battery_id])}

@router.post("/missions/{mission_id}/cancel")
def cancel_mission(mission_id: str):
    item = safe(lambda: get_store().update("missions", mission_id, {"status": "CANCELLED"}))
    if not item: raise HTTPException(404, "Mission not found")
    return item

@router.post("/maintenance/{item_id}/complete")
def complete_maintenance(item_id: str):
    item = safe(lambda: get_store().update("maintenance", item_id, {"status": "COMPLETED"}))
    if not item: raise HTTPException(404, "Maintenance item not found")
    return item

@router.post("/maintenance/{item_id}/cancel")
def cancel_maintenance(item_id: str):
    item = safe(lambda: get_store().update("maintenance", item_id, {"status": "CANCELLED"}))
    if not item: raise HTTPException(404, "Maintenance item not found")
    return item
